"""Shared code for rose plots of Owen et al. 2017 read from their outlines (Supp. Fig. 11, one rose per
cell, black outlines; Fig. 4A inset, navy outlines given as CONFIG["outline"], searched only inside
CONFIG["region"]). Loaded with hash pinning by the reading files, which give a CONFIG.
(_rose.py, for Fig. 4B and S14D, tells outlines from the axis line by colour; in S11 both are black.)

All positions are found in the image; the only things typed in are the printed value of the
outer ring (CONFIG["rings"]: the values of the rings, increasing outwards; MATLAB's polar axes draw
the rings at equal steps from 0, so with two rings and the label of the outer one printed, the
inner ring is half of it) and the fill colour.
- centre: the row of the long dark horizontal axis line (0 deg to 180 deg): the row with most
  dark pixels (or, for a mid-grey axis line, pixels darker than CONFIG["axis_dark"]); the column of the light-grey vertical spoke (90 deg) above it.
- hub: the dark disc where all outlines meet: the first radius at which less than 60% of a circle
  around the centre is dark.
- rings: walking straight down from the centre, 14 px beside the 270 deg spoke, the runs of grid
  grey beyond the hub (runs thinner than 0.6 of the thickest are stray anti-aliased pixels and are
  dropped; if more remain than rings, the set evenly spaced from the centre is kept); matched in order to CONFIG["rings"]; value = a + b * radius, fitted
  through them and the centre (value 0); misfit = the largest residual in pixels.
- bins: on circles of radius 1.3 to 2.0 times the hub radius (or CONFIG["cross_frac"] times the
  first ring's radius, where outlines near a small hub blur into the fill), the dark outline
  crossings every 0.1 deg, except within 3 px of the axis line. The bin width is the widest equal division of
  360 deg (8 to 120 bins) whose grid the crossings agree with (mean resultant of the angles folded
  by the width at least 0.85 of the best); the phase is their circular mean.
- value of a bin: walking out along the bin's centre ray, the farthest dark OUTLINE pixel within
  the outer ring (plus the outline width) is the wedge's end, its radius converted by the ring fit.
  The blue fill is not used: in these roses it was drawn by filling the whole outline path as one
  polygon, so it spans chords between neighbouring wedge tips and lies outside the wedges in places
  (Supp. Fig. 11, roses 9 and 16). A wedge ending inside the hub is reported as at most the hub.
  Only the dark connected component through the centre (outline and axis line) is used, so printed
  labels (the ring label; a stray "30" angle label in rose 13) are never taken for a wedge. A wedge
  whose outline crosses a circle just outside the outer ring within its bin is cut by the plot
  box: no value, "more than" the outer ring in the note.
  The rings are searched from at least 60 px out (where the spokes beside 270 deg have diverged).
  Interval: half the outline width, 1 px and twice the ring misfit.
Angles in degrees counter-clockwise from 0 deg (right).
"""
import numpy as np


def read(k, image, C):
    if C.get("region"):  # an inset: search only inside (c0, r0, c1, r1)
        c0, r0, c1, r1 = C["region"]
        out = read(k, image[r0:r1, c0:c1], {kk: v for kk, v in C.items() if kk != "region"})
        for p in out:
            p["px"] = [p["px"][0] + c0, p["px"][1] + r0]
        return out
    img = k.rgb(image)
    g = img.mean(axis=2)
    sat = img.max(axis=2) - img.min(axis=2)
    fill = k.color_mask(image, C["fill"], C.get("fill_tol", 40)) & (sat > 25)
    dark = (g < C.get("dark", 110)) & (sat < 40)
    if C.get("outline"):  # coloured outlines (Fig. 4A inset) count as outline too
        dark |= k.color_mask(image, C["outline"], C.get("outline_tol", 45)) & (sat > 20)  # not neutral grey text halos
    grid = (sat < 20) & (g > 195) & (g < 232)
    H, W = g.shape
    # a mid-grey axis line (Fig. 3G inset) is found with a higher threshold, used for nothing else
    axis_dark = dark | ((g < C.get("axis_dark", 0)) & (sat < 40))
    row0 = float(np.argmax(axis_dark.sum(axis=1)))
    upper = grid[: max(int(row0) - 40, 1), :]
    cols = upper.sum(axis=0)
    cand = np.where(cols > 0.8 * cols.max())[0]
    col0 = float(np.mean(k.clusters(cand)[0])) if len(cand) else float(np.argmax(cols))
    # outline half-width: the axis line's thickness at the far right of the centre
    th = [b - a + 1 for a, b in k.runs(dark[:, min(int(col0) + int(0.45 * W), W - 1)], 1)]
    half_out = (min(th, key=lambda t: abs(t - 6)) if th else 6) / 2.0
    # the rose outline and the axis line are one connected shape through the centre; printed
    # labels (ring values, a stray angle label) are separate and dropped
    from scipy import ndimage
    lab, _ = ndimage.label(dark, structure=np.ones((3, 3)))
    cl = lab[max(int(row0) - 15, 0):int(row0) + 16, max(int(col0) - 15, 0):int(col0) + 16]  # the commonest within 15 px
    keep = np.bincount(cl[cl > 0]).argmax() if (cl > 0).any() else 0
    dark = lab == keep if keep else dark
    hub = 0
    ang = np.radians(np.arange(0, 360, 2))
    for r in range(3, 300):
        rr = (row0 - r * np.sin(ang)).astype(int)
        cc = (col0 + r * np.cos(ang)).astype(int)
        ok = (rr >= 0) & (rr < H) & (cc >= 0) & (cc < W)
        if dark[rr[ok], cc[ok]].mean() < 0.6:
            hub = r
            break
    off = 14
    col = int(round(col0)) + off
    start = int(row0) + max(hub, 60) + 3  # near the centre the 240/300 deg spokes pass beside the 270 deg one
    down = grid[start:, col - 1:col + 2].any(axis=1)
    runs_ = k.clusters(np.where(down)[0], 2)
    thick = max((b - a + 1 for a, b in runs_), default=0)
    runs_ = [(a, b) for a, b in runs_ if b - a + 1 >= 0.6 * thick]  # rings are drawn at one width; stray anti-aliased pixels are thinner
    rings = [float(np.hypot((a + b) / 2 + start - row0, off)) for a, b in runs_]
    if len(rings) > len(C["rings"]):
        rings = k.even_subset([0.0] + rings, len(C["rings"]) + 1)[1:] or rings
    if len(rings) != len(C["rings"]):
        raise RuntimeError(f"rings: expected {len(C['rings'])}, found {rings}")
    R = k.Lin(list(zip(rings, C["rings"])) + [(0.0, 0.0)])
    angs = []
    radii = [f * rings[0] for f in C["cross_frac"]] if C.get("cross_frac") else [f * hub for f in (1.3, 1.5, 1.7, 2.0)]
    for rad in radii:
        a = np.arange(0, 360, 0.1)
        rr = np.round(row0 - rad * np.sin(np.radians(a))).astype(int)
        cc = np.round(col0 + rad * np.cos(np.radians(a))).astype(int)
        on = dark[rr, cc] & (np.abs(rr - row0) > half_out + 3)
        for s, e in k.clusters(np.where(on)[0], 3):
            angs.append(((s + e) / 2) * 0.1)
    angs = np.sort(np.array(angs))
    if C.get("bin_deg"):
        width = float(C["bin_deg"])
    else:
        score = {n: abs(np.mean(np.exp(1j * 2 * np.pi * angs * n / 360))) for n in range(8, 121)}
        best = max(score.values())
        width = 360.0 / min(n for n, s in score.items() if s > 0.85 * best)
    ph = np.angle(np.mean(np.exp(1j * 2 * np.pi * angs / width))) * width / (2 * np.pi)
    out = []
    for i in range(int(round(360 / width))):
        th_ = (ph + (i + 0.5) * width) % 360
        t = np.radians(th_)
        last = None
        for r in range(hub, int(rings[-1] + 2 * half_out + 4)):
            y = int(round(row0 - r * np.sin(t)))
            x = int(round(col0 + r * np.cos(t)))
            if not (0 <= y < H and 0 <= x < W):
                break
            if dark[y, x]:
                last = r
        # a wedge past the outer ring: its radial outline edges cross a circle just outside the ring
        rc = rings[-1] + 2 * half_out + 6
        aa = np.radians(np.arange(th_ - width / 2 + 0.5, th_ + width / 2 - 0.5, 0.1))
        yy = np.round(row0 - rc * np.sin(aa)).astype(int)
        xx = np.round(col0 + rc * np.cos(aa)).astype(int)
        ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W) & (np.abs(yy - row0) > half_out + 3)
        cut = bool(dark[yy[ok], xx[ok]].any())
        e = half_out + 1 + 2 * R.misfit_px
        px = [col0 + (last or hub) * np.cos(t), row0 - (last or hub) * np.sin(t)]
        if cut:
            out.append({"x": round(float(th_), 3), "y": None, "px": px,
                        "note": f"outline runs past the outer ring and is cut by the plot box: more than {C['rings'][-1]}; bin {width:.4g} deg"})
            continue
        if last is None or last <= hub + 2:
            out.append({"x": round(float(th_), 3), "y": float(R.val(hub)) / 2, "lo": 0.0, "hi": float(R.val(hub)),
                        "px": px, "note": f"wedge ends inside the hub: at most {R.val(hub):.3g}; bin {width:.4g} deg"})
            continue
        out.append({"x": round(float(th_), 3), "y": float(R.val(last)), "lo": max(0.0, float(R.val(last - e))),
                    "hi": float(R.val(last + e)), "px": px,
                    "note": f"bin {width:.4g} deg; centre ({col0:.0f}, {row0:.0f}); hub {hub} px; rings {[round(v) for v in rings]} px; ring misfit {R.misfit_px:.2g} px"})
    out.sort(key=lambda p: p["x"])
    return out
