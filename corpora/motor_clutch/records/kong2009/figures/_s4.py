"""Shared reading code for Fig. S4: filled black squares on an L-shaped pair of axes with
outward ticks. In panel A the squares (one per repeat) overlap into a band; in panel B four
squares are joined by straight lines.

Everything is found in the rendered crop; a reading file supplies only the printed tick
labels it matched."""

import numpy as np
from scipy import ndimage as ndi

import _lt


def _y_ticks(black, ycols, xrows, min_len=12):
    """Rows of the outward ticks on the left of the y axis, down to the x axis (squares drawn
    against the axis on its right do not hide them, so unlike `_lt.y_ticks` the right side is not
    looked at)."""
    c0 = ycols[0]
    H = xrows[1] + 4
    left = np.zeros(H, int)
    for r in range(H):
        k = 0
        while c0 - 1 - k >= 0 and black[r, c0 - 1 - k]:
            k += 1
        left[r] = k
    groups = [(s, e) for s, e in _lt._runs(left >= min_len) if e - s >= 3]
    th = np.median([e - s for s, e in groups])
    groups = [(s, e) for s, e in groups if 0.5 * th <= e - s <= 2.0 * th]
    return [(s + e - 1) / 2 for s, e in groups]


def _setup(image, y_labels, x_labels):
    black = _lt.mask_for(image, "black")
    ycols, xrows = _lt.find_axes(black)
    ya = _lt.YAxis(_y_ticks(black, ycols, xrows), [list(y_labels)])
    xc = _lt.x_ticks(black, ycols, xrows)
    if len(xc) != len(x_labels):
        raise ValueError(f"found {len(xc)} x ticks at columns {[round(c) for c in xc]}, expected {len(x_labels)}")
    xa = _lt.Linear(list(zip(sorted(xc), x_labels)))
    seg = ya.segs[0]
    inside = black.copy()
    inside[:, :ycols[1] + 3] = False  # the y axis and what is left of it
    inside[xrows[0] - 2:, :] = False  # the x axis and what is below it
    return black, inside, ycols, xrows, xa, seg, ya.misfit_px, xa.misfit_px


def _marker_size(inside, line):
    """The side of a filled square: what survives an opening wider than the joining lines,
    measured as the median height of the separate blobs."""
    k = max(3, 3 * line)
    op = ndi.binary_opening(inside, structure=np.ones((k, k), bool))
    lab, n = ndi.label(op)
    hs = [s[0].stop - s[0].start for s in ndi.find_objects(lab)]
    ws = [s[1].stop - s[1].start for s in ndi.find_objects(lab)]
    return op, lab, n, hs, ws


def read_band(image, at, y_labels, x_labels):
    """Panel A: the band of overlapping squares, read at the given repeat numbers. The squares
    are centred on their values, so at a column the band runs from the highest value within half a
    square's width plus half a square, to the lowest minus half a square: its centre is the value
    to within half the band's height less half a square."""
    black, inside, ycols, xrows, xa, seg, ymis, xmis = _setup(image, y_labels, x_labels)
    line = ycols[1] - ycols[0] + 1
    op, lab, n, hs, ws = _marker_size(inside, line)
    # the side of one square: the isolated squares near the start of the series (the narrowest
    # blobs; the band is one wide blob)
    single = [h for h, w in zip(hs, ws) if w < 1.6 * h and h > 4 * line]
    s = float(np.median(single))
    per_px = abs(seg.b)
    out = []
    for x in at:
        c = int(round(xa.px(x)))
        runs = _lt._runs(op[:, c])
        if not runs:
            out.append({"x": x, "y": None, "note": "no band at this column"})
            continue
        a, b = max(runs, key=lambda se: se[1] - se[0])
        mid = (a + b - 1) / 2
        half = max(0.0, (b - a - s) / 2) + 2 + ymis
        y = seg.value(mid)
        out.append({"x": x, "y": float(y), "lo": float(y - half * per_px), "hi": float(y + half * per_px),
                    "px": [float(c), float(mid)], "px_lo": float(mid - half), "px_hi": float(mid + half),
                    "note": f"band rows {a}-{b - 1} ({b - a} px) at column {c}; one square is {s:.0f} px"})
    return out


def read_squares(image, at, y_labels, x_labels):
    """Panel B: each filled square's centre."""
    black, inside, ycols, xrows, xa, seg, ymis, xmis = _setup(image, y_labels, x_labels)
    line = ycols[1] - ycols[0] + 1
    op, lab, n, hs, ws = _marker_size(inside, line)
    # a square cut by the y axis keeps only its right part: its centre is its right edge less half
    # the side of the whole squares
    sides = [h for h in hs if h > 4 * line]
    s = float(np.median(sides))
    per_x = abs(xa.b)
    per_y = abs(seg.b)
    out = []
    for sl in ndi.find_objects(lab):
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        if h < 4 * line:
            continue
        row = (sl[0].start + sl[0].stop - 1) / 2
        note = f"square rows {sl[0].start}-{sl[0].stop - 1}, columns {sl[1].start}-{sl[1].stop - 1}"
        if w < 0.85 * h:
            col = sl[1].stop - 1 - (s - 1) / 2
            note += f"; cut by the y axis, centre taken {s / 2:.0f} px left of its right edge"
            ex = 3.0
        else:
            col = (sl[1].start + sl[1].stop - 1) / 2
            ex = 0.0
        ty = 2 + ymis
        x, y = float(xa.value(col)), float(seg.value(row))
        out.append({"x": round(x, 2), "y": y, "lo": y - ty * per_y, "hi": y + ty * per_y,
                    "px": [float(col), float(row)], "px_lo": row - ty, "px_hi": row + ty,
                    "note": note + f"; x to within {(2 + xmis + ex) * per_x:.1f}"})
    return sorted(out, key=lambda r: r["x"])
