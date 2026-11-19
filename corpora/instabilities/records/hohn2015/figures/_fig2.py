"""Shared reading code for the three panels of Fig. 2 (PDF p. 2), MATLAB-style boxed plots.

Calibration: the plot box is the four long dark lines. The tick marks point inwards from all four
sides of the box and are mirrored (bottom/top, left/right), so a tick is a short dark run that
leaves the box edge on both opposite sides at the same position; curves that touch one edge do not
make a tick. The ticks found are matched in order to the printed labels the caller passes, and the
linear fit of label against pixel is checked (largest misfit returned).

Curve: the representative embryo is the only red line (the other embryos are blue, cyan and green,
the guide band of (a) is light grey). In a narrow band of columns around the x position, the red
pixels are collected; the reading is the middle of their vertical extent, and the 95% interval is
that extent widened by the calibration misfit and one pixel. Where the curve is steep, the extent is
long and the interval honest about it. In (b) the open red circles on the curve widen the extent
symmetrically about the curve. A column without red pixels (the line hidden under another embryo's,
or outside the red line's time span) gives no value.
"""
import numpy as np


def _runs(v):
    out, start = [], None
    for i, x in enumerate(list(v) + [False]):
        if x and start is None:
            start = i
        elif not x and start is not None:
            out.append((start, i))
            start = None
    return out


def _longest(v, gap):
    best, bs, be = 0, 0, 0
    start, last = None, None
    for i, x in enumerate(list(v) + [False] * (gap + 2)):
        if x:
            if start is None:
                start = i
            last = i
        elif start is not None and i - last > gap:
            if last + 1 - start > best:
                best, bs, be = last + 1 - start, start, last + 1
            start = None
    return best, bs, be


def _edges(dark, axis_len, frac=0.6):
    """Indices of lines (rows of `dark`) with a dark run of at least frac of the length."""
    gap = max(2, axis_len // 300)
    return [i for i in range(dark.shape[0]) if _longest(dark[i], gap)[0] >= frac * axis_len]


def _group(idx):
    groups, cur = [], []
    for i in sorted(idx) + [None]:
        if cur and (i is None or i != cur[-1] + 1):
            groups.append(cur)
            cur = []
        if i is not None:
            cur.append(i)
    return groups


def box(image):
    # black and grey ink: every channel low (the blue embryo lines are not dark in this sense,
    # the light grey band of (a) is above the threshold)
    im = image.astype(int)
    hi, lo = im.max(axis=2), im.min(axis=2)
    neutral = hi - lo < 40
    dark = (hi < 200) & neutral  # neutral ink, down to thin anti-aliased tick marks
    frame = (hi < 140) & neutral  # the box lines themselves
    H, W = dark.shape
    rows = _group(_edges(frame, W, 0.6))
    cols = _group(_edges(frame.T, H, 0.5))  # curves crossing a side line break it into pieces
    if len(rows) < 2 or len(cols) < 2:
        raise ValueError("plot box not found")
    top, bot = rows[0], rows[-1]
    left, right = cols[0], cols[-1]
    return dark, (left[-1] + 1, top[-1] + 1, right[0], bot[0])  # interior c0, r0, c1, r1


def _ticks_from_edge(strip, lo, hi, thick):
    """Positions where a short dark run starts at the edge of the strip (first rows)."""
    n = strip.shape[0]
    lengths = []
    for j in range(strip.shape[1]):
        k = 0
        while k < 2 and k < n and not strip[k, j]:
            k += 1
        m = 0
        while k + m < n and strip[k + m, j]:
            m += 1
        lengths.append(m if k <= 1 else 0)
    good = [j for j, m in enumerate(lengths) if lo <= m <= hi]
    return [(g[0] + g[-1]) / 2 + 0.5 for g in _group(good) if len(g) <= thick]


def ticks(dark, b):
    c0, r0, c1, r1 = b
    w, h = c1 - c0, r1 - r0
    lo_x, hi_x = max(1, h // 150), max(3, h // 15)
    lo_y, hi_y = max(1, w // 150), max(3, w // 15)
    thick = max(3, (w + h) // 250)  # a tick mark is thin against the box
    bottom = _ticks_from_edge(dark[r1 - 1::-1, c0:c1], lo_x, hi_x, thick)
    top = _ticks_from_edge(dark[r0:, c0:c1], lo_x, hi_x, thick)
    left = _ticks_from_edge(dark[r0:r1, c0:].T, lo_y, hi_y, thick)
    right = _ticks_from_edge(dark[r0:r1, c1 - 1::-1].T, lo_y, hi_y, thick)
    tol = max(2.0, w / 300)

    def both(a, bb):
        return [(x + min(bb, key=lambda y: abs(y - x))) / 2 for x in a if bb and min(abs(y - x) for y in bb) <= tol]

    xt = [c0 + x for x in both(bottom, top)]
    yt = [r0 + y for y in both(left, right)]
    sides = {"bottom": [c0 + x for x in bottom], "top": [c0 + x for x in top],
             "left": [r0 + y for y in left], "right": [r0 + y for y in right]}
    return xt, yt, sides


def fit(pix, labels):
    if len(pix) != len(labels):
        raise ValueError(f"found {len(pix)} ticks for {len(labels)} labels: {pix}")
    p, v = np.array(pix), np.array(labels, float)
    b, a = np.polyfit(p, v, 1)
    misfit = float(np.max(np.abs(p - (v - a) / b)))
    return a, b, misfit


def calibrate(image, x_labels, y_labels, y_frame=None):
    """x_labels, y_labels: the values of the ticks found, in order (unlabelled ticks between
    labelled ones are included at their evenly spaced values). y_frame: (top value, bottom value)
    when a label is printed level with the top or bottom line of the box; those lines are then
    marks too (None for a side without such a label), and the y ticks are taken from whichever
    side shows them (some are lost under the embryo lines)."""
    dark, b = box(image)
    xt, yt, sides = ticks(dark, b)
    ax, bx, mx = fit(sorted(xt), sorted(x_labels))
    if y_frame is None:
        ay, by, my = fit(sorted(yt), sorted(y_labels, reverse=True))  # rows grow downwards
    else:
        top_v, bot_v = y_frame
        tol = max(2.0, (b[2] - b[0]) / 300)
        cand = sorted(set(round(y, 1) for y in sides["left"] + sides["right"]))
        merged = []
        for y in cand:
            if merged and y - merged[-1][-1] <= tol:
                merged[-1].append(y)
            else:
                merged.append([y])
        found = [float(np.mean(g)) for g in merged]
        ys = sorted(y_labels, reverse=True)
        pix, vals = [], []
        if top_v is not None:
            pix.append(b[1] - 0.5)
            vals.append(top_v)
        if bot_v is not None:
            pix.append(b[3] + 0.5)
            vals.append(bot_v)
        # the ticks found are the lowest labels, in order from the bottom
        found = found[-len(ys):] if len(found) > len(ys) else found
        for p, v in zip(found[::-1], ys[::-1]):
            pix.append(p)
            vals.append(v)
        ay, by, my = fit(pix, vals)
    return dict(box=b, ax=ax, bx=bx, mx=mx, ay=ay, by=by, my=my, xt=xt, yt=yt)


def red_mask(image):
    im = image.astype(int)
    r, g, bl = im[..., 0], im[..., 1], im[..., 2]
    return (r > 170) & (r - g > 110) & (r - bl > 110)


def read_red(image, at, x_labels, y_labels, note="", y_frame=None):
    cal = calibrate(image, x_labels, y_labels, y_frame)
    c0, r0, c1, r1 = cal["box"]
    red = red_mask(image)
    red[:, :c0 + 2] = False
    red[:, c1 - 2:] = False
    red[:r0 + 2] = False
    red[r1 - 2:] = False
    half = max(1, int(round((c1 - c0) / 400)))
    out = []
    pad = cal["my"] + 1.0
    for x in at:
        col = (x - cal["ax"]) / cal["bx"]
        cs = int(round(col))
        band = red[:, max(0, cs - half):cs + half + 1]
        rows = np.nonzero(band.any(axis=1))[0]
        if len(rows) == 0:
            out.append({"x": x, "y": None, "note": "no red pixels at this time: the red line is hidden or absent"})
            continue
        top, bot = float(rows.min()), float(rows.max() + 1)
        mid = (top + bot) / 2
        y = cal["ay"] + cal["by"] * mid
        y_a = cal["ay"] + cal["by"] * (top - pad)
        y_b = cal["ay"] + cal["by"] * (bot + pad)
        out.append({"x": x, "y": float(y), "lo": float(min(y_a, y_b)), "hi": float(max(y_a, y_b)),
                    "px": [float(col), float(mid)], "px_lo": top, "px_hi": bot,
                    "note": f"{note}calibration misfit x {cal['mx']:.2f} px, y {cal['my']:.2f} px"})
    return out
