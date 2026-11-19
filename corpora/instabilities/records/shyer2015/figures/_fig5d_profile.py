"""Fig. 5D (PDF p. 7), upper right: anti-SHH staining intensity against distance (uM) across the 100 um box,
E13 in blue, E15 in red, each with a pale shaded band (the SD). An embedded raster of about 300 dpi rendered
at 1200 dpi, so 4 px blocks.

Grey level g = brightest channel. The y axis is the pale grey vertical line (g < 215) with the longest run
right of column 200 (the micrograph at the far left is excluded). Ticks are the row groups where the 5 px
left of the axis are pale ink (g < 240): one tick per unit. The printed labels 8, 6, 4, 2 are found as the
dark text (g < 100) in the band of columns 15-115 px left of the axis (the rotated axis title lies further
left); each label's row centre is matched
to the nearest tick, a first line is fitted to those, every tick is given the value the line rounds it to,
and the final line is fitted to all the ticks; its rms misfit (px) widens every interval.

x: no tick marks are drawn on the x axis, so the printed labels 20, 40, 60, 80, 100 are the marks: each is
the column centre of a dark text group (columns within 60 px joined, so "100" is one group) in the band of
rows 30-160 px below the x axis (the lowest long pale horizontal line); groups narrower than 30 px are the
dashed epithelial-border line crossing the axis and are dropped; a line is fitted, its misfit widens every interval, and the note reports where the y axis
falls (it should read 0).

Curve: the line pixels are the saturated colour (blue: B > 150, R < 100, G < 140; red: R > 180, G < 100,
B < 100); the shaded bands are pale and not matched. At each x the columns within +-(WIN_UM um + the x misfit in px) are read: in
each, the centre of the line's pixels; y is the median of those centres. The traces are noisy, so the
interval runs from the lowest to the highest line pixel in the window (the trace's own scatter and line
width), widened by the misfit. Where fewer than a third of the window's columns show the colour (blue hidden
under red, where the red is drawn on top), the value is not read.
"""

import numpy as np

WIN_UM = 0.5


def _groups(idx, gap=1):
    out = []
    for i in idx:
        if out and i - out[-1][-1] <= gap:
            out[-1].append(int(i))
        else:
            out.append([int(i)])
    return out


def _longest(v):
    best = cur = 0
    for b in v:
        cur = cur + 1 if b else 0
        best = max(best, cur)
    return best


def _fit(px, val):
    px = np.asarray(px, float)
    val = np.asarray(val, float)
    b, a = np.polyfit(px, val, 1)
    mis = max(float(np.sqrt(np.mean(((val - (a + b * px)) / b) ** 2))), 0.5)
    return float(a), float(b), mis


def calibrate(image):
    im = np.asarray(image)[..., :3].astype(int)
    g = im.max(axis=2)
    H, W = g.shape
    pale = g < 215
    runs = np.array([_longest(pale[:, c]) if c > 200 else 0 for c in range(W)])
    c0 = int(np.argmax(runs))
    while pale[:, c0 - 1].sum() > 0.5 * runs[c0]:
        c0 -= 1
    # the x axis: lowest row whose pale run right of the y axis exceeds half the width
    hr = [r for r in range(H) if _longest(g[r, c0:] < 240) > 0.5 * (W - c0)]
    xrow = max(hr)
    tick_rows = [r for r in range(H) if (g[r, c0 - 6:c0 - 1] < 240).all()]
    ticks = [(t[0] + t[-1]) / 2.0 for t in _groups(tick_rows) if len(t) <= 16]
    # printed y labels
    band = g[:, max(c0 - 115, 0):c0 - 15] < 100
    lab_rows = [r for r in range(H) if band[r].any()]
    labs = [(t[0] + t[-1]) / 2.0 for t in _groups(lab_rows, gap=3) if len(t) > 30]
    labs = [l for l in labs if l < xrow]
    values = [8, 6, 4, 2][-len(labs):] if len(labs) <= 4 else None
    if values is None or len(labs) != 4:
        raise RuntimeError(f"expected 4 y labels, found {labs}")
    near = [min(ticks, key=lambda t: abs(t - l)) for l in labs]
    a, b, _ = _fit(near, values)
    tv = [round(a + b * t) for t in ticks]
    ya, yb, ymis = _fit(ticks, tv)
    # printed x labels: column centres of the text groups below the x axis
    xb = g[xrow + 30:min(xrow + 160, H), :] < 100
    cols = [c for c in range(c0 + 40, W) if xb[:, c].any()]
    xl = [(t[0] + t[-1]) / 2.0 for t in _groups(cols, gap=60) if t[-1] - t[0] > 30]
    if len(xl) != 5:
        raise RuntimeError(f"expected 5 x labels, found {xl}")
    xa, xbb, xmis = _fit(xl, [20, 40, 60, 80, 100])
    return {"c0": c0, "xrow": xrow, "ya": ya, "yb": yb, "ymis": ymis, "xa": xa, "xb": xbb, "xmis": xmis,
            "ticks": ticks, "tick_vals": tv, "xlabels": xl}


def read(image, at, colour):
    im = np.asarray(image)[..., :3].astype(int)
    R, G, B = im[..., 0], im[..., 1], im[..., 2]
    if colour == "blue":
        mask = (B > 150) & (R < 100) & (G < 140)
    else:
        mask = (R > 180) & (G < 100) & (B < 100)
    cal = calibrate(image)
    y_of = lambda r: cal["ya"] + cal["yb"] * r          # noqa: E731
    col_of = lambda x: (x - cal["xa"]) / cal["xb"]       # noqa: E731
    win = WIN_UM / cal["xb"] + cal["xmis"]   # the x calibration's misfit widens the window
    x_at_axis = cal["xa"] + cal["xb"] * cal["c0"]
    base = (f"y ticks {len(cal['ticks'])} (values {cal['tick_vals'][0]}..{cal['tick_vals'][-1]}), misfit "
            f"{cal['ymis']:.2f} px; x from label centres, misfit {cal['xmis']:.2f} px, y axis at x = {x_at_axis:.2f}")
    out = []
    for xv in at:
        x = float(xv)
        cx = col_of(x)
        c_lo, c_hi = int(round(cx - win)), int(round(cx + win))
        centres, tops, bots = [], [], []
        for c in range(c_lo, c_hi + 1):
            rows = np.where(mask[:cal["xrow"], c])[0]
            if len(rows):
                centres.append((rows.min() + rows.max()) / 2.0)
                tops.append(rows.min())
                bots.append(rows.max())
        n = c_hi - c_lo + 1
        if len(centres) < n / 3.0:
            out.append({"x": x, "y": None, "note": f"{colour} line not visible at columns {c_lo}-{c_hi} "
                        f"({len(centres)} of {n} columns): hidden under the other trace; " + base})
            continue
        r = float(np.median(centres))
        t = min(tops) - cal["ymis"]
        bt = max(bots) + cal["ymis"]
        out.append({"x": x, "y": float(y_of(r)), "lo": float(min(y_of(t), y_of(bt))), "hi": float(max(y_of(t), y_of(bt))),
                    "px": [float(cx), r], "px_lo": float(min(tops)), "px_hi": float(max(bots)),
                    "note": f"{colour} line in columns {c_lo}-{c_hi}: median centre row {r:.1f}, pixels rows "
                            f"{min(tops)}-{max(bots)}; " + base})
    return out
