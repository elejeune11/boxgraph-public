"""Shared code for the rose plots (polar histograms of velocity angles) of Owen et al. 2017
(Fig. 4B, S14D). Loaded with hash pinning by the reading files, which give a CONFIG.

All positions are found in the image; the only things typed in are the printed values of the
rings (CONFIG["rings"], increasing outwards; MATLAB draws them at equal steps) and the colours.
- centre: the row of the long dark horizontal axis line (0 deg to 180 deg), and the column of
  the light-grey vertical spoke (90 deg) found above it; their crossing.
- rings: walking straight down from the centre, 14 px beside the 270 deg spoke (wedges there are
  short), the runs of grid grey beyond the hub are the rings (radius from the centre), matched in order to CONFIG["rings"]; value = a + b * radius,
  fitted, misfit = the largest residual in pixels.
- bins: on circles of radius 1.2 to 1.6 times the hub radius, the wedge outlines (dark blue)
  are found every 0.1 deg. The bin width is the widest equal division of 360 deg (8 to 120 bins)
  whose grid the outline angles agree with (mean resultant of the angles folded by the width at
  least 0.85 of the best); the phase of the grid is their circular mean. Bins cover 360 deg.
- value of a bin: walking out along the bin's centre ray, the last pixel of wedge fill or
  outline (gaps up to 4 px bridged, any gap within 25 px of the hub, where the converging
  outlines blend the colours) is the wedge's end; its radius converted by the ring fit.
  A bin whose wedge ends inside the hub (the dark disc where all outlines meet) is reported as at
  most the hub radius. Interval: the outline half-width, 1 px and twice the ring misfit.
Angles are in degrees, counter-clockwise from the 0 deg label (right), as printed on the plot.
"""
import numpy as np


def read(k, image, C):
    """CONFIG["region"] (c0, r0, c1, r1), if given, restricts the search to an inset."""
    if C.get("region"):
        c0, r0, c1, r1 = C["region"]
        out = read(k, image[r0:r1, c0:c1], {kk: v for kk, v in C.items() if kk != "region"})
        for p in out:
            p["px"] = [p["px"][0] + c0, p["px"][1] + r0]
        return out
    img = k.rgb(image)
    g = img.mean(axis=2)
    sat = img.max(axis=2) - img.min(axis=2)
    sat0 = img.max(axis=2) - img.min(axis=2)
    fill = k.color_mask(image, C["fill"], C.get("fill_tol", 35)) & (sat0 > 25)  # not the grey grid
    outline = k.color_mask(image, C["outline"], C.get("outline_tol", 45)) & (sat0 > 25)
    grid = (sat < 20) & (g > 195) & (g < 232)
    axis = (sat < 40) & (g < 130) & ~outline
    H, W = g.shape
    rows = [(axis[r, :].sum(), r) for r in range(H)]
    row0 = float(max(rows)[1])
    # vertical spoke above the centre: the column with most grid pixels in the upper part
    upper = grid[: int(row0) - 40, :]
    cols = upper.sum(axis=0)
    col0 = float(np.argmax(cols))
    cand = np.where(cols > 0.8 * cols.max())[0]
    col0 = float(np.mean(k.clusters(cand)[0])) if len(cand) else col0
    # hub radius: dark outline disc around the centre
    hub, inside = 0, False
    for r in range(3, 300):
        ang = np.radians(np.arange(0, 360, 2))
        rr = (row0 - r * np.sin(ang)).astype(int)
        cc = (col0 + r * np.cos(ang)).astype(int)
        ok = (rr >= 0) & (rr < H) & (cc >= 0) & (cc < W)
        frac = outline[rr[ok], cc[ok]].mean()
        if frac >= 0.6:
            inside = True
        elif inside:
            hub = r
            break
    # rings straight down
    off = 14  # beside the 270 deg spoke, which is itself grid grey
    col = int(round(col0)) + off
    down = grid[int(row0) + hub + 3:, col - 1:col + 2].any(axis=1)
    rings = [float(np.hypot((a + b) / 2 + hub + 3, off)) for a, b in k.clusters(np.where(down)[0], 2)]
    if len(rings) > len(C["rings"]):  # a stray grey run (a wedge edge): keep the evenly spaced set
        rings = k.even_subset(rings, len(C["rings"])) or rings
    if len(rings) != len(C["rings"]):
        raise RuntimeError(f"rings: expected {len(C['rings'])}, found {rings}")
    R = k.Lin(list(zip(rings, C["rings"])) + ([(0.0, 0.0)] if C.get("origin_zero", True) else []))
    # bin grid from outline crossings
    angs = []
    for f in (1.2, 1.4, 1.6):
        rad = f * hub
        a = np.arange(0, 360, 0.1)
        rr = np.round(row0 - rad * np.sin(np.radians(a))).astype(int)
        cc = np.round(col0 + rad * np.cos(np.radians(a))).astype(int)
        on = outline[rr, cc] & ~axis[rr, cc]
        for s, e in k.clusters(np.where(on)[0], 3):
            angs.append(((s + e) / 2) * 0.1)
    angs = np.sort(np.array(angs))
    width = float(C["bin_deg"]) if C.get("bin_deg") else None
    if width is None:  # the widest equal division of 360 deg that the outline angles agree with
        score = {n: abs(np.mean(np.exp(1j * 2 * np.pi * angs * n / 360))) for n in range(8, 121)}
        best = max(score.values())
        width = 360.0 / min(n for n, s in score.items() if s > 0.85 * best)
    ph = np.angle(np.mean(np.exp(1j * 2 * np.pi * angs / width))) * width / (2 * np.pi)
    out = []
    half_out = 2.0
    nb = int(round(360 / width))
    for i in range(nb):
        th = (ph + (i + 0.5) * width) % 360
        t = np.radians(th)
        last = None
        gap = 0
        for r in range(hub, int(rings[-1]) + 10):
            y = int(round(row0 - r * np.sin(t)))
            x = int(round(col0 + r * np.cos(t)))
            if not (0 <= y < H and 0 <= x < W):
                break
            if fill[y, x] or outline[y, x]:
                last = r
                gap = 0
            elif r > hub + 25:  # next to the hub the wedges blend with the converging outlines
                gap += 1
                if gap > 4 and last is not None:
                    break
        e = half_out + 1 + 2 * R.misfit_px
        px = [col0 + (last or hub) * np.cos(t), row0 - (last or hub) * np.sin(t)]
        if last is None or last <= hub + 2:
            out.append({"x": round(float(th), 3), "y": float(R.val(hub)) / 2, "lo": 0.0, "hi": float(R.val(hub)),
                        "px": px, "note": f"wedge ends inside the hub: at most {R.val(hub):.3g}; bin {width:.4g} deg"})
            continue
        out.append({"x": round(float(th), 3), "y": float(R.val(last)), "lo": float(R.val(last - e)),
                    "hi": float(R.val(last + e)), "px": px,
                    "note": f"bin {width:.4g} deg; centre ({col0:.0f}, {row0:.0f}); hub {hub} px; rings {[round(v) for v in rings]} px; ring misfit {R.misfit_px:.2g} px"})
    out.sort(key=lambda p: p["x"])
    return out
