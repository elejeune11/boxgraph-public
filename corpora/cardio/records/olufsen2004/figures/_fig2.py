"""Shared reading code for Fig. 2 (PDF p. 8): tau versus R, with six horizontal time-scale lines.

Calibration, all from the image:
  * the plot box is the black frame (the longest dark rows and columns); its edges are the axis
    limits printed at the corners (x: 0 and 1.5 cm; y: 0 and 0.25);
  * the interior tick marks are short black runs hanging down from the top edge (x: 0.5, 1) and
    pointing left from the right edge (y: 0.05, 0.1, 0.15, 0.2); they are matched to the printed
    labels in order and the misfit of a straight-line fit is carried into every interval.
Curves are found by colour: pure blue (tau), pure red (flow time-scales), pure green (pressure
time-scales). Each value is the centre of the coloured run in the pixel column of the x position.
"""
import numpy as np

X_LABELS = [0.0, 0.5, 1.0, 1.5]          # printed under the x axis, left to right
Y_LABELS = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25]  # printed beside the y axis, bottom to top


def _runs(v):
    idx = np.nonzero(v)[0]
    if idx.size == 0:
        return []
    cuts = np.nonzero(np.diff(idx) > 1)[0]
    starts = np.r_[idx[0], idx[cuts + 1]]
    ends = np.r_[idx[cuts], idx[-1]]
    return list(zip(starts.tolist(), ends.tolist()))


def ink(image):
    im = image.astype(float)
    return (im.max(axis=2) < 110)  # black: all channels dark


def colour(image, which):
    im = image.astype(float)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    if which == "blue":
        return (b > 150) & (r < 110) & (g < 110)
    if which == "red":
        return (r > 150) & (g < 110) & (b < 110)
    if which == "green":
        return (g > 150) & (r < 110) & (b < 110)
    raise ValueError(which)


def _frame(k):
    H, W = k.shape
    row_len = k.sum(axis=1)
    col_len = k.sum(axis=0)
    rows = np.nonzero(row_len > 0.6 * W)[0]
    cols = np.nonzero(col_len > 0.6 * H)[0]
    top = [r for r in rows if r < rows.min() + 10]
    bot = [r for r in rows if r > rows.max() - 10]
    left = [c for c in cols if c < cols.min() + 10]
    right = [c for c in cols if c > cols.max() - 10]
    return (np.mean(top) + 0.5, np.mean(bot) + 0.5, np.mean(left) + 0.5, np.mean(right) + 0.5,
            max(top) + 1, min(bot), max(left) + 1, min(right))


def _fit(marks):
    p = np.array([m[0] for m in marks])
    v = np.array([m[1] for m in marks])
    b, a = np.polyfit(p, v, 1)
    misfit = float(np.max(np.abs(p - (v - a) / b)))
    return a, b, max(misfit, 0.5)


def calibrate(image):
    k = ink(image)
    top, bot, left, right, top_in, bot_in, left_in, right_in = _frame(k)
    # x ticks: short black runs straight down from the inside of the top edge
    xt = []
    for c in range(int(left_in) + 3, int(right_in) - 3):
        n = 0
        while k[top_in + n, c]:
            n += 1
        if 8 <= n <= 80:
            xt.append(c)
    xt = [(s + e) / 2 + 0.5 for s, e in _runs(np.isin(np.arange(k.shape[1]), xt))]
    # y ticks: short black runs leftwards from the inside of the right edge
    yt = []
    for r in range(int(top_in) + 3, int(bot_in) - 3):
        n = 0
        while k[r, right_in - 1 - n]:
            n += 1
        if 8 <= n <= 80:
            yt.append(r)
    yt = [(s + e) / 2 + 0.5 for s, e in _runs(np.isin(np.arange(k.shape[0]), yt))]
    if len(xt) != len(X_LABELS) - 2 or len(yt) != len(Y_LABELS) - 2:
        raise ValueError(f"unexpected ticks: x {xt}, y {yt}")
    xm = [(left, X_LABELS[0])] + list(zip(xt, X_LABELS[1:-1])) + [(right, X_LABELS[-1])]
    ym = [(bot, Y_LABELS[0])] + list(zip(sorted(yt, reverse=True), Y_LABELS[1:-1])) + [(top, Y_LABELS[-1])]
    xa, xb, xmis = _fit(xm)
    ya, yb, ymis = _fit(ym)
    return {"xa": xa, "xb": xb, "xmis": xmis, "ya": ya, "yb": yb, "ymis": ymis,
            "box": (left_in, top_in, right_in, bot_in), "k": k}


def col_of(cal, x):
    return (x - cal["xa"]) / cal["xb"]


def val_of_row(cal, row):
    return cal["ya"] + cal["yb"] * row


def runs_in_col(mask, col, r0, r1):
    return [(s + r0, e + r0) for s, e in _runs(mask[r0:r1, col])]
