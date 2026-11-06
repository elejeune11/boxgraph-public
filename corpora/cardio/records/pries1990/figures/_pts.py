"""Shared reading code for the point plots of Pries et al. 1990 (Figs. 2, 5, 6, 7).

Everything is found in the image:
- the frame of the plot box: the rows and columns that are mostly ink;
- tick marks: short ink runs sticking out of a frame line (outwards), thinner than a marker;
  they are matched to the printed labels in order, and where a label stands at a frame line
  (0 and 1 of an axis drawn from 0 to 1) the frame line itself is that label's position;
- markers: ink blobs larger than a line. Open circles and triangles are filled first (small
  enclosed holes), then a morphological opening with a disk wider than any line removes the
  lines and leaves the markers. A marker is open if most of its inside was a hole, filled if not.
  A blob much larger than one marker (overlapping markers) is split into as many markers as its
  area holds.
"""

import numpy as np
from scipy import ndimage as ndi
from scipy.cluster.vq import kmeans2


def dark(image):
    g = image.astype(float).mean(axis=2)
    paper = float(np.percentile(g, 60))
    ink = float(np.percentile(g, 0.5))
    return g < (paper + ink) / 2


def groups(idx):
    out = []
    for i in idx:
        if out and i == out[-1][1] + 1:
            out[-1][1] = i
        else:
            out.append([i, i])
    return [tuple(g) for g in out]


def frame(d, frac=0.45):
    """The plot box: (top, bottom) row bands and (left, right) column bands, each (first, last)."""
    H, W = d.shape
    rows = groups(list(np.nonzero(d.mean(axis=1) >= frac)[0]))
    top, bottom = rows[0], rows[-1]
    inner = d[top[0]:bottom[1] + 1, :]
    cols = groups(list(np.nonzero(inner.mean(axis=0) >= 0.7)[0]))
    left, right = cols[0], cols[-1]
    return {"top": top, "bottom": bottom, "left": left, "right": right}


def _run_lengths(d, edge, fr, extent=120):
    """For each position along the edge, the ink run through the frame line, outwards; minus the
    line thickness (the median run)."""
    H, W = d.shape
    out = {}
    if edge in ("bottom", "top"):
        band = fr[edge]
        positions = range(fr["left"][1] + 3, fr["right"][0] - 2)
        for c in positions:
            if edge == "bottom":
                r = band[0] - 6
                while r <= band[1] + 6 and not d[r, c]:
                    r += 1
                n = 0
                while r < H and d[r, c] and n < extent:
                    n += 1
                    r += 1
            else:
                r = band[1] + 6
                while r >= band[0] - 6 and not d[r, c]:
                    r -= 1
                n = 0
                while r >= 0 and d[r, c] and n < extent:
                    n += 1
                    r -= 1
            out[c] = n
    else:
        band = fr[edge]
        positions = range(fr["top"][1] + 3, fr["bottom"][0] - 2)
        for r in positions:
            if edge == "left":
                c = band[1] + 6
                while c >= band[0] - 6 and not d[r, c]:
                    c -= 1
                n = 0
                while c >= 0 and d[r, c] and n < extent:
                    n += 1
                    c -= 1
            else:
                c = band[0] - 6
                while c <= band[1] + 6 and not d[r, c]:
                    c += 1
                n = 0
                while c < W and d[r, c] and n < extent:
                    n += 1
                    c += 1
            out[r] = n
    base = float(np.median(list(out.values())))
    return {p: max(0, int(n - base)) for p, n in out.items()}, base


def ticks(d, edge, fr, min_len=8, max_width=None):
    """Tick marks on one frame edge: (centre position, length), thin runs only."""
    lengths, base = _run_lengths(d, edge, fr)
    if max_width is None:
        max_width = int(3 * base) + 4
    pos = [p for p, n in sorted(lengths.items()) if n >= min_len]
    out = []
    for a, b in groups(pos):
        if b - a + 1 <= max_width:
            out.append(((a + b) / 2.0, max(lengths[q] for q in range(a, b + 1))))
    return out, base


def fit(pos, vals):
    pos, vals = np.asarray(pos, float), np.asarray(vals, float)
    A = np.vstack([np.ones_like(pos), pos]).T
    coef, *_ = np.linalg.lstsq(A, vals, rcond=None)
    res = vals - A @ coef
    misfit_px = float(np.max(np.abs(res / coef[1]))) if len(pos) > 2 else 0.0
    return coef, misfit_px


def axis(d, fr, edge, labels, frame_labels=None, min_len=8, pick=None):
    """Calibrate one axis. labels: the printed tick labels in image order (left to right, or top
    to bottom). frame_labels: {frame band name: printed value} for labels standing at a frame line.
    pick: optional function choosing the ticks to use from those found (e.g. the longest ones)."""
    t, base = ticks(d, edge, fr, min_len=min_len)
    # a frame line continuing past the corner looks like a tick next to it: not a tick
    ends = ("left", "right") if edge in ("top", "bottom") else ("top", "bottom")
    t = [p for p in t if all(abs(p[0] - (fr[e][0] + fr[e][1]) / 2.0) > 15 for e in ends)]
    if pick is not None:
        t = pick(t)
    if len(t) != len(labels):
        raise ValueError(f"{edge}: found {len(t)} ticks {[(round(p), n) for p, n in t]}, expected {len(labels)}")
    pos = [p for p, _ in t]
    vals = list(labels)
    for name, v in (frame_labels or {}).items():
        a, b = fr[name]
        pos.append((a + b) / 2.0)
        vals.append(v)
    coef, mis = fit(pos, vals)
    return {"coef": coef, "misfit_px": mis, "ticks": pos, "values": vals, "line_px": base}


def to_val(ax, p):
    return float(ax["coef"][0] + ax["coef"][1] * p)


def to_px(ax, v):
    return (v - ax["coef"][0]) / ax["coef"][1]


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def markers(d, fr, diameter, open_r, margin=None, ring_max=1.0):
    """Markers in the plot box (and on its frame lines). diameter: a marker's diameter in px, used
    for the hole size, the split area and the inner test; open_r: radius of the opening disk (wider
    than any line, narrower than a marker)."""
    if margin is None:
        margin = diameter
    margin = int(margin)
    r0, r1 = max(0, fr["top"][0] - margin), min(d.shape[0], fr["bottom"][1] + margin + 1)
    c0, c1 = max(0, fr["left"][0] - margin), min(d.shape[1], fr["right"][1] + margin + 1)
    sub = d[r0:r1, c0:c1]
    filled_all = ndi.binary_fill_holes(sub)
    holes = filled_all & ~sub
    lab, n = ndi.label(holes)
    areas = ndi.sum(holes, lab, index=np.arange(1, n + 1))
    a_marker = np.pi * (diameter / 2.0) ** 2
    keep = np.zeros(n + 1, bool)
    keep[1:] = (areas >= 0.04 * a_marker) & (areas <= 0.8 * a_marker)
    small_holes = keep[lab]
    solid = sub | small_holes
    opened = ndi.binary_opening(solid, structure=disk(open_r))
    lab2, n2 = ndi.label(opened)
    hlab, nh = ndi.label(small_holes)
    R = diameter / 2.0
    yy, xx = np.mgrid[0:sub.shape[0], 0:sub.shape[1]]
    out = []
    for k in range(1, n2 + 1):
        m = lab2 == k
        area = int(m.sum())
        if area < 0.35 * a_marker:
            continue
        rr, cc = np.nonzero(m)
        nsplit = max(1, int(round(area / (0.92 * a_marker))))
        if nsplit == 1:
            centres = [(rr.mean(), cc.mean())]
        else:
            pts = np.vstack([rr, cc]).T.astype(float)
            cen, _ = kmeans2(pts, nsplit, minit="++", seed=0)
            centres = [tuple(c) for c in cen]
        # the small holes inside this blob, each given to its nearest centre
        hid = sorted(set(hlab[m].ravel()) - {0})
        given = {i: [] for i in range(len(centres))}
        for h in hid:
            hr, hc = np.nonzero(hlab == h)
            hcen = (hr.mean(), hc.mean())
            i = int(np.argmin([(hcen[0] - a) ** 2 + (hcen[1] - b) ** 2 for a, b in centres]))
            given[i].append((hr, hc))
        bbox = [int(cc.min()) + c0, int(rr.min()) + r0, int(cc.max()) + c0, int(rr.max()) + r0]
        blob = []
        for i, (r, c) in enumerate(centres):
            if given[i]:
                # open marker: its centre is the centre of the hole it encloses
                hr = np.concatenate([g[0] for g in given[i]])
                hc = np.concatenate([g[1] for g in given[i]])
                r, c = float(hr.mean()), float(hc.mean())
                kd, score = "open", float(len(hr)) / a_marker
            else:
                # filled marker: mean shift on the blob's ink, then the disk must be solid ink
                for _ in range(6):
                    w = m & ((yy - r) ** 2 + (xx - c) ** 2 <= R * R)
                    if not w.any():
                        break
                    wr, wc = np.nonzero(w)
                    r, c = float(wr.mean()), float(wc.mean())
                rho2 = (yy - r) ** 2 + (xx - c) ** 2
                score = float(sub[rho2 <= (0.42 * diameter) ** 2].mean())
                # a marker is round: a ring just outside it is mostly paper (lines cross it in
                # narrow arcs), while a wedge where curves meet keeps going
                ring = (rho2 >= (0.65 * diameter) ** 2) & (rho2 <= (0.75 * diameter) ** 2)
                for j, (ro, co) in enumerate(centres):
                    if j != i:  # an overlapping neighbour marker is not counted against this one
                        ring &= (yy - ro) ** 2 + (xx - co) ** 2 > (0.6 * diameter) ** 2
                ring_ink = float(sub[ring].mean())
                kd = "filled" if (score >= 0.92 and ring_ink <= ring_max) else "rejected"
                score = (score, ring_ink)
            blob.append({"row": r + r0, "col": c + c0, "area": area, "n_in_blob": nsplit,
                         "kind": kd, "score": score, "bbox": bbox})
        # a blob that did not resolve into markers (one part rejected: ink where lines meet) leaves
        # its solid parts in doubt; open markers keep their own hole and stay
        if any(b["kind"] == "rejected" for b in blob):
            for b in blob:
                if b["kind"] == "filled":
                    b["kind"] = "rejected"
        out += blob
    return sorted(out, key=lambda m: (m["col"], m["row"]))


def longest(t, frac=0.75):
    """The long tick marks (labelled ones), dropping short ones and markers sitting on an axis."""
    mx = max(n for _, n in t)
    return [p for p in t if p[1] >= frac * mx]


def read_points(image, x_spec, y_spec, diameter, open_r, want, exclude=None, at=None, at_tol=None):
    """Read the markers of one kind ('filled' or 'open').
    x_spec, y_spec: dict(edge=..., labels=[...], frame_labels={...}, pick=fn) for axis().
    exclude: (x_min, x_max, y_min, y_max) in data units, a region not to read (a legend).
    at: x positions to read (the marker of that kind nearest each, within at_tol in x units);
    without it every marker of that kind is returned at the x read from the image."""
    d = dark(image)
    fr = frame(d)
    ax = axis(d, fr, **x_spec)
    ay = axis(d, fr, **y_spec)
    ms = markers(d, fr, diameter, open_r)
    pts = []
    for m in ms:
        if m["kind"] != want:
            continue
        x, y = to_val(ax, m["col"]), to_val(ay, m["row"])
        boxes = [] if not exclude else ([exclude] if not isinstance(exclude[0], (tuple, list)) else exclude)
        if any(b[0] <= x <= b[1] and b[2] <= y <= b[3] for b in boxes):
            continue
        pts.append((x, m))
    cal = f"x misfit {ax['misfit_px']:.1f} px, y misfit {ay['misfit_px']:.1f} px"
    if at is None:
        return [point(ax, ay, m, diameter, note=cal) for x, m in sorted(pts, key=lambda p: p[0])]
    out = []
    for a in at:
        near = [(abs(x - a), x, m) for x, m in pts if abs(x - a) <= at_tol]
        if not near:
            out.append({"x": a, "y": None, "note": f"no {want} marker within {at_tol} of x = {a}"})
            continue
        near.sort(key=lambda t: t[0])
        if len(near) > 1 and near[1][0] - near[0][0] < 0.5 * at_tol:
            out.append({"x": a, "y": None, "note": f"two {want} markers near x = {a}"})
            continue
        _, x, m = near[0]
        r = point(ax, ay, m, diameter, note=f"marker x read {x:.4f}; {cal}")
        r["x"] = a
        out.append(r)
    return out


def point(ax_x, ax_y, m, diameter, extra_px=0.0, note=""):
    """A reading for one marker: value at its centre with a 95% interval from the centroid
    precision (2 px), the y calibration misfit, and for markers split out of an overlap a quarter
    of a diameter."""
    err = 2.0 + 2.0 * ax_y["misfit_px"] + extra_px + (diameter / 4.0 if m["n_in_blob"] > 1 else 0.0)
    row, col = m["row"], m["col"]
    y = to_val(ax_y, row)
    lo, hi = sorted([to_val(ax_y, row + err), to_val(ax_y, row - err)])
    x = to_val(ax_x, col)
    nt = f"marker at col {col:.0f} row {row:.0f}; +-{err:.1f} px"
    if m["n_in_blob"] > 1:
        nt += f"; split from a blob of {m['n_in_blob']} overlapping markers"
    if note:
        nt += "; " + note
    return {"x": x, "y": y, "lo": lo, "hi": hi, "px": [float(col), float(row)],
            "px_lo": float(row - err), "px_hi": float(row + err), "note": nt}
