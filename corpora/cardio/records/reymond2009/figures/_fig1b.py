"""Shared reading code for Fig. 1B (PDF p. 4): normalized elastance against normalized time,
vector graphics rendered at 1400 dpi. Two curves: E*N 'isovolumic' (black) and EN 'measured'
(gray, drawn over the black one).

Calibration, all from the image:
- the y axis is the column band where more than 30% of the rows are dark (gray < 90); the x axis
  is the row band where more than 50% of the columns are dark;
- the one labelled y tick ('1') is the short horizontal dark run 15 px left of the y axis, above
  the x axis; the one labelled x tick ('1') is the short vertical dark run 15 px below the x axis,
  right of the y axis; exactly one of each is required;
- the axes carry only the labels 1 and a single '0' under the corner. The reading takes x = 0 at
  the y axis and y = 0 at the x axis (a reading choice, q_fig1b_origin). With two marks per axis
  there is no misfit to measure; 1 px is allowed for where each mark is placed.

The gray curve: pixels with 105 < gray < 190 and channel spread < 30, opened with a 7 x 7 square
(removing the anti-aliased rims of black ink and text); the largest connected component is the
curve. The black curve: dark pixels (gray < 90) inside the plot (8 px clear of the axes); the
largest connected component is the curve (text glyphs are separate, smaller components); it is
visible only where it leaves the gray curve. At each requested x, exactly one run of the curve's
component in that column is required; the value is its centre. With t the line's thickness (the
median run height where the curve is flat), the interval is 1 px + 1 px calibration + |slope| x
1 px + half the excess of the run over t*sqrt(1+slope^2) (a run cut or extended by the other
curve).
"""

import numpy as np
from scipy import ndimage


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def calibrate(image):
    im = image[..., :3].astype(float)
    g = im.mean(axis=2)
    dark = g < 90
    rb = _runs(dark.mean(axis=1) > 0.5)
    cb = _runs(dark.mean(axis=0) > 0.3)
    if len(rb) != 1 or not cb:
        raise RuntimeError(f"axes: rows {rb}, cols {cb}")
    xr0, xr1 = rb[0]
    yc0, yc1 = cb[0]
    yt = [(a + b - 1) / 2 for a, b in _runs(dark[:xr0, yc0 - 15]) if b - a < 30]
    xt = [(a + b - 1) / 2 for a, b in _runs(dark[xr1 + 15, yc1:]) if b - a < 30]
    if len(yt) != 1 or len(xt) != 1:
        raise RuntimeError(f"ticks: y {yt}, x {xt}")
    x0 = (yc0 + yc1 - 1) / 2.0
    x1 = yc1 + xt[0]
    y0 = (xr0 + xr1 - 1) / 2.0
    y1 = yt[0]
    return dict(g=g, im=im, dark=dark, x0=x0, x1=x1, y0=y0, y1=y1,
                box=(yc1 + 8, 0, image.shape[1], xr0 - 8))


def _largest(mask):
    lab, n = ndimage.label(mask, structure=np.ones((3, 3)))
    if n == 0:
        raise RuntimeError("no curve found")
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    return lab == (1 + int(np.argmax(sizes)))


def curve_mask(cal, which):
    g, im = cal["g"], cal["im"]
    c0, r0, c1, r1 = cal["box"]
    if which == "gray":
        spread = im.max(axis=2) - im.min(axis=2)
        m = (g > 105) & (g < 190) & (spread < 30)
        m = ndimage.binary_opening(m, structure=np.ones((7, 7)))
    else:
        m = cal["dark"].copy()
    m[:, :c0] = False
    m[r1:, :] = False
    return _largest(m)


def read(image, at, which):
    cal = calibrate(image)
    m = curve_mask(cal, which)
    sx = cal["x1"] - cal["x0"]
    sy = cal["y1"] - cal["y0"]

    def runs(c):
        return _runs(m[:, c]) if 0 <= c < m.shape[1] else []

    hs = []
    for c in range(0, m.shape[1] - 12, 6):
        a, b = runs(c), runs(c + 12)
        if len(a) == 1 and len(b) == 1 and abs(sum(a[0]) - sum(b[0])) / 24.0 < 0.05:
            hs.append(a[0][1] - a[0][0])
    t = float(np.median(hs)) if hs else 20.0
    out = []
    for x in at:
        col = cal["x0"] + x * sx
        c = int(round(col))
        rr = runs(c)
        nb = [runs(k) for k in (c - 10, c + 10)]
        if len(rr) != 1 or not all(len(n) == 1 for n in nb):
            out.append({"x": x, "y": None, "note": f"{len(rr)} runs of the curve in this column"})
            continue
        a, b = rr[0]
        row = (a + b - 1) / 2.0
        sl = abs(sum(nb[1][0]) - sum(nb[0][0])) / 40.0
        expected = t * np.sqrt(1 + sl * sl)
        e = 1.0 + 1.0 + sl * 1.0 + abs((b - a) - expected) / 2.0
        y = (row - cal["y0"]) / sy
        lo = (row + e - cal["y0"]) / sy
        hi = (row - e - cal["y0"]) / sy
        out.append({"x": x, "y": y, "lo": min(lo, hi), "hi": max(lo, hi), "px": [col, row],
                    "px_lo": row - e, "px_hi": row + e,
                    "note": f"run {b - a} px (line {t:.0f} px, expected {expected:.0f}); slope {sl:.2f}; "
                            "two-mark calibration, y = 0 at the x axis"})
    return out
