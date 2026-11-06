"""Fig. S12E (PDF p. 55): correlation coefficient against pixel shift for a synthetic
kymograph: the open squares (the tracking algorithm's output) and the red fitted
Gaussian.

Calibration, from the image: the plot box is the longest grey lines; the tick
strokes under the bottom edge are matched to the labels -5 ... 5 and the strokes
left of the box to the labels -0.4 ... 1 (strokes kept where an evenly spaced
tick belongs, so text cannot pass for one).
Squares: dark, near-neutral connected outlines about as wide as tall and hollow,
one per tick column; the centre of the outline's bounding box is the point.
WHICH = "curve" reads the red curve instead, at the tick positions: the median
row of red pixels in a narrow column; at shift 0 the red vertical line covers
the curve, so it is not read there.
"""
import numpy as np
from scipy import ndimage as ndi
from scipy.ndimage import uniform_filter1d

WHICH = "squares"
X_LABELS = [-5.0, -4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0]   # matched, left to right
Y_LABELS = [-0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0]                     # matched, bottom to top


def _minima(prof, depth, win=41):
    base = uniform_filter1d(prof, win)
    d = base - prof
    out = []
    for i in range(4, len(prof) - 4):
        if d[i] > depth and d[i] == d[i - 3:i + 4].max():
            w = np.clip(d[i - 4:i + 5], 0, None)
            pos = (np.arange(i - 4, i + 5) * w).sum() / w.sum()
            if out and pos - out[-1][0] < 8:
                if d[i] > out[-1][1]:
                    out[-1] = (pos, d[i])
                continue
            out.append((pos, d[i]))
    return out


def _peak(prof, lo, hi):
    i = lo + int(np.argmax(prof[lo:hi]))
    win = np.arange(max(lo, i - 3), min(hi, i + 4))
    wt = prof[win]
    return float((win * wt).sum() / wt.sum())


def _even(cands, lo_pos, hi_pos, n):
    """Strokes nearest n evenly spaced positions from lo_pos to hi_pos."""
    out = []
    for k in range(n):
        want = lo_pos + k * (hi_pos - lo_pos) / (n - 1)
        near = [c for c in cands if abs(c - want) < 0.15 * abs(hi_pos - lo_pos) / (n - 1)]
        out.append(min(near, key=lambda c: abs(c - want)) if near else None)
    return out


def _calibrate(img):
    f = img.astype(float)
    g = f.mean(axis=2)
    sat = f.max(axis=2) - f.min(axis=2)
    h, w = g.shape
    grey = ((sat < 40) & (g < 200)).astype(float)
    cols = grey[int(0.2 * h):int(0.8 * h)].mean(axis=0)
    left = _peak(cols, int(0.1 * w), int(0.3 * w))
    right = _peak(cols, int(0.85 * w), w)
    rows = grey[:, int(left) + 20:int(right) - 20].mean(axis=1)
    top = _peak(rows, 0, int(0.2 * h))
    bottom = _peak(rows, int(0.75 * h), int(0.95 * h))
    # x ticks below the bottom edge: the outermost lie on the box's left and right edges
    xs = [c for c, d in _minima(g[int(bottom) + 15:int(bottom) + 50].mean(axis=0), 10)]
    xm = [(p, v) for p, v in zip(_even(xs, left, right, len(X_LABELS)), X_LABELS) if p is not None]
    # y ticks left of the box: the outermost at the box's bottom and top
    ys = [r for r, d in _minima(g[:, int(left) - 50:int(left) - 15].mean(axis=1), 10)]
    ym = [(p, v) for p, v in zip(_even(ys, bottom, top, len(Y_LABELS)), Y_LABELS) if p is not None]
    X, Y = np.array(xm), np.array(ym)
    bx, ax = np.polyfit(X[:, 1], X[:, 0], 1)
    by, ay = np.polyfit(Y[:, 1], Y[:, 0], 1)
    return dict(ax=ax, bx=bx, ay=ay, by=by, n_x=len(X), n_y=len(Y),
                misfit_x=float(np.max(np.abs(X[:, 0] - (ax + bx * X[:, 1])))),
                misfit_y=float(np.max(np.abs(Y[:, 0] - (ay + by * Y[:, 1])))),
                left=left, right=right, top=top, bottom=bottom)


def read(image, at):
    return read_which(image, WHICH)


def read_which(image, which):
    cal = _calibrate(image)
    f = image.astype(float)
    g = f.mean(axis=2)
    sat = f.max(axis=2) - f.min(axis=2)
    yv = lambda r: (r - cal["ay"]) / cal["by"]
    unit = abs(cal["by"])
    note = f"x {cal['n_x']} marks misfit {cal['misfit_x']:.2f} px; y {cal['n_y']} marks misfit {cal['misfit_y']:.2f} px"
    out = []
    if which == "squares":
        dark = (g < 100) & (sat < 60)
        # bridge short horizontal gaps: at shift 0 the red vertical line cuts the square's top and bottom
        dark = ndi.binary_closing(dark, structure=np.ones((1, 25), bool))
        lab, n = ndi.label(dark)
        objs = ndi.find_objects(lab)
        squares = []
        for i, sl in enumerate(objs, start=1):
            hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
            if 35 <= hh <= 110 and 35 <= ww <= 110 and abs(hh - ww) < 0.15 * max(hh, ww):
                fill = (lab[sl] == i).mean()
                if fill < 0.5:                                   # hollow: an outline, not a glyph
                    squares.append(((sl[1].start + sl[1].stop - 1) / 2.0, (sl[0].start + sl[0].stop - 1) / 2.0))
        for v in X_LABELS:
            c = cal["ax"] + cal["bx"] * v
            near = [s for s in squares if abs(s[0] - c) < 0.3 * abs(cal["bx"])]
            if not near:
                out.append({"x": v, "y": None, "note": "no square found at this shift"})
                continue
            sc, sr = min(near, key=lambda s: abs(s[0] - c))
            y = yv(sr)
            e = (2.0 + cal["misfit_y"]) / unit
            out.append({"x": float((sc - cal["ax"]) / cal["bx"]), "y": float(y), "lo": float(y - e),
                        "hi": float(y + e), "px": [sc, sr], "note": "square centre; " + note})
    else:
        red = (f[..., 0] > 180) & (f[..., 1] < 120) & (f[..., 2] < 120)
        colfrac = red[int(cal["top"]) + 10:int(cal["bottom"]) - 10].mean(axis=0)
        vertical = colfrac > 0.5                                  # the two red vertical lines
        for v in X_LABELS:
            c = int(round(cal["ax"] + cal["bx"] * v))
            if vertical[c - 12:c + 13].any():
                continue                                          # the red vertical line covers the curve here
            rr = np.where(red[int(cal["top"]):int(cal["bottom"]), c - 2:c + 3].any(axis=1))[0]
            if len(rr) == 0:
                out.append({"x": v, "y": None, "note": "curve not found"})
                continue
            r = float(np.median(rr)) + int(cal["top"])
            y = yv(r)
            e = (0.5 * (rr.max() - rr.min()) + 2.0 + cal["misfit_y"]) / unit
            out.append({"x": v, "y": float(y), "lo": float(y - e), "hi": float(y + e), "px": [c, r],
                        "note": "red curve centre; " + note})
    return out
