"""Fig. 6(b) (PDF p. 19): the upper branch of the solid blue curve bounding the region of intrinsic
volume conservation in the (K0 h^2, H0 h) plane.

Calibration, all from the image (black = every channel below 60): the horizontal axis is the row
holding the longest black run, the vertical axis the column holding the longest black column run.
x ticks are columns where black stands at least 15 px both above and below the horizontal axis
(within 30 px; grouped) with the axis line running on 40 px either side (not the arrowhead): three are found, the left one (labelled -16/9), the vertical axis itself
(K0 h^2 = 0, where the H0 h axis stands) and the right one (labelled omega = 64/9). y ticks are rows
where black stands at least 15 px left and right of the vertical axis: five are found, labelled
(top to bottom) sqrt(omega) = 8/3, 1, the horizontal axis (H0 h = 0), -1 and -sqrt(omega). The
fraction labels are matched as the numbers they print. Both axes are fitted by straight lines; the
largest misfit is reported.

The blue curve: pixels within 40 (RGB distance) of (51, 51, 255), opened by a 7 x 7 square, which
removes the thin hatching of the same colour and keeps the boundary stroke (and the slivers of it
left visible beside a red dash, which an opening must not erase: the run kept is then at least 2 px
but the opening's 7 px applies across the stroke, so a sliver thinner than 7 px vertically
counts as hidden). The stroke's width w is the median length of the top blue run over the clear,
nearly flat stretch 1 <= K0 h^2 <= 3; h = w sqrt(1 + slope^2). The red dashed line
(255, 0, 0) of (H0)^2 = K0 is drawn over the blue curve where the two run together (K0 h^2 > about 2).
At each x the curve is predicted from the neighbouring columns (a parabola through the centres of
the topmost opened blue runs within 60 columns that no red touches), and the blue stroke is found in
the raw colour mask (not opened, so that a sliver beside a red dash counts) within h of that
prediction:
  its upper edge free (no red in the 2 px above it): the centre is h/2 below the edge, +- 2.5 px
    (edge +-1 px, width +-1 px; hatching only touches the stroke from below);
  else its lower edge free: the centre is h/2 above that edge, +- 2.5 px;
  no blue visible (wholly under a red dash): the red run there, less half the blue stroke on each
    side, widened by 2 px.
Intervals are widened by the y misfit + 1 px and |slope| times (x misfit + 0.5 px).
Near the tip (K0 h^2 < -1.4) the curve is steep and is not read.
"""

import numpy as np
from scipy import ndimage

HATCH = 7  # opening size: wider than the hatching lines, narrower than the boundary stroke
BLUE = (51, 51, 255)
RED = (255, 0, 0)


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _longest(v):
    return max((b - a for a, b in _runs(v)), default=0)


def _mask(image, col, tol=40.0):
    d = np.sqrt(((image[..., :3].astype(float) - np.array(col, float)) ** 2).sum(axis=2))
    return d < tol


def _fit(pix, vals):
    k, m = np.polyfit(np.asarray(pix, float), np.asarray(vals, float), 1)
    mis = float(np.max(np.abs((np.asarray(vals) - m) / k - np.asarray(pix))))
    return m, k, mis


def calibrate(image):
    black = (image[..., :3] < 60).all(axis=2)
    H, W = black.shape
    r = int(np.argmax([_longest(black[i]) for i in range(H)]))
    c = int(np.argmax([_longest(black[:, j]) for j in range(W)]))
    xf = [black[r - 30:r - 4, j].sum() >= 15 and black[r + 5:r + 30, j].sum() >= 15 for j in range(W)]
    xt = [(a + b - 1) / 2.0 for a, b in _runs(xf) if b - a <= 15]
    # a tick lies on the axis line, which runs on 40 px past it (this leaves out the arrowhead)
    xt = [t for t in xt if black[r, int(t) - 40:int(t) + 41].all()]
    yf = [black[i, c - 30:c - 4].sum() >= 15 and black[i, c + 5:c + 30].sum() >= 15 for i in range(H)]
    yt = [(a + b - 1) / 2.0 for a, b in _runs(yf) if b - a <= 15]
    if len(xt) != 3 or len(yt) != 5:
        raise ValueError(f"ticks: x {xt}, y {yt}")
    xa, xb, xm = _fit(xt, [-16 / 9, 0.0, 64 / 9])
    ya, yb, ym = _fit(yt, [8 / 3, 1.0, 0.0, -1.0, -8 / 3])
    return (xa, xb, xm), (ya, yb, ym), r


def read(image, at):
    (xa, xb, xm), (ya, yb, ym), axis_row = calibrate(image)
    blue = ndimage.binary_opening(_mask(image, BLUE), structure=np.ones((HATCH, HATCH)))
    red = _mask(image, RED)
    raw = _mask(image, BLUE)

    def top(col):
        rr = [(a, b - 1) for a, b in _runs(blue[:axis_row - 5, col]) if b - a >= 2]
        return rr[0] if rr else None

    # the stroke's width, from the clear stretch 1 <= K0 h^2 <= 3 (no red dash on it, nearly flat)
    W = blue.shape[1]
    lens = []
    for k in range(int(round((1 - xa) / xb)), int(round((3 - xa) / xb))):
        t = top(k)
        if t is not None:
            lens.append(t[1] - t[0] + 1)
    w0 = float(np.median(lens))
    out = []
    for x in at:
        cx = (x - xa) / xb
        c = int(round(cx))
        if x < -1.4:
            out.append({"x": x, "y": None, "note": "steep tip: not read"})
            continue
        nb = []
        for k in range(c - 60, c + 61):
            if k == c or k < 0 or k >= W:
                continue
            t = top(k)
            if t is not None and not red[max(t[0] - 3, 0), k] and not red[t[1] + 3, k]:
                nb.append((k, (t[0] + t[1]) / 2.0, t[1] - t[0] + 1))
        if len(nb) < 10:
            out.append({"x": x, "y": None, "note": "too few clear blue columns nearby"})
            continue
        ks = np.array([p[0] for p in nb], float)
        ys = np.array([p[1] for p in nb], float)
        P = np.polyfit(ks, ys, 2)
        pred = float(np.polyval(P, cx))
        slope = float(np.polyval(np.polyder(P), cx))
        w = w0
        h = w * np.sqrt(1 + slope * slope)
        # raw blue runs (not opened) near the prediction
        near = [(a, b - 1) for a, b in _runs(raw[:axis_row - 5, c])
                if b - 1 >= pred - h and a <= pred + h]
        a_top = near[0][0] if near else None
        b_bot = near[-1][1] if near else None
        if a_top is not None and not red[a_top - 1, c] and not red[a_top - 2, c]:
            # the stroke's upper edge is free: the centre is half a stroke below it
            yc = a_top + h / 2.0
            lo, hi = yc - 2.5, yc + 2.5
            state = "upper edge of the blue stroke"
        elif b_bot is not None and not red[b_bot + 1, c] and not red[b_bot + 2, c]:
            yc = b_bot - h / 2.0
            lo, hi = yc - 2.5, yc + 2.5
            state = "lower edge of the blue stroke (upper edge under a red dash)"
        else:
            rr = [(a, b - 1) for a, b in _runs(red[:axis_row - 5, c]) if a - 2 * h <= pred <= b - 1 + 2 * h]
            if not rr:
                out.append({"x": x, "y": None, "note": "blue stroke not found and no red dash over it"})
                continue
            a, b = min(rr, key=lambda q: abs((q[0] + q[1]) / 2.0 - pred))
            lo, hi = a + h / 2.0 - 2.0, b - h / 2.0 + 2.0
            if hi < lo:
                lo, hi = (a + b) / 2.0 - 2.0, (a + b) / 2.0 + 2.0
            yc = (lo + hi) / 2.0
            state = "blue stroke wholly under a red dash"
        pad = ym + 1.0 + abs(slope) * (xm + 0.5)
        lo, hi = lo - pad, hi + pad
        v, v1, v2 = ya + yb * yc, ya + yb * lo, ya + yb * hi
        out.append({"x": x, "y": float(v), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                    "px": [float(cx), float(yc)], "px_lo": float(lo), "px_hi": float(hi),
                    "note": f"{state}; stroke {w:.0f} px; x misfit {xm:.1f} px, y misfit {ym:.1f} px"})
    return out
