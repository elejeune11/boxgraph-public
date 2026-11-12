"""Fig. 3 (p. 4): histogram of capillary segment lengths, 20 um bins from 0 to 200 um; read the height of
each bar (number of capillary segments) at the bin centres.

Calibration, all from the image:
- the y axis is the long vertical dark line at the left of the plot; its tick marks stick out to its left.
  The ticks are evenly spaced (major ticks at the labels 0, 10, ..., 50 and minor ticks halfway between);
  the lowest tick lies on the x axis line and is matched to the label 0, the topmost to the label 50, and
  the ticks in between are matched in order at 5 per tick. A straight line is fitted through all eleven.
- the x axis is the long horizontal dark line; its ticks stick out below it, at the labels 0, 20, ... 200
  (eleven ticks; labels printed every 40). A straight line is fitted through them.
Bars: in each bin's centre column, the bar's top outline is the first dark run met going down from the top
of the plot; its centre row is the value. The 95% interval is the half-thickness of the outline plus twice
the calibration misfit (rms), plus half a pixel.
"""
import numpy as np

DARK = 100


def _runs(v):
    """(start, end) of runs of True in a boolean vector (end inclusive)."""
    out, start = [], None
    for i, b in enumerate(v):
        if b and start is None:
            start = i
        elif not b and start is not None:
            out.append((start, i - 1))
            start = None
    if start is not None:
        out.append((start, len(v) - 1))
    return out


def _fit(px, val):
    px, val = np.asarray(px, float), np.asarray(val, float)
    a, b = np.polyfit(px, val, 1)
    rms = float(np.sqrt(np.mean((a * px + b - val) ** 2)))
    return a, b, rms


def read(image, at):
    gray = np.asarray(image, float)[..., :3].mean(axis=2)
    dark = gray < DARK
    h, w = dark.shape

    # axis lines: the column and row with the most dark pixels
    cs, rs = dark.sum(axis=0), dark.sum(axis=1)
    ycols = [c for c in range(w // 3) if cs[c] > 0.8 * cs[: w // 3].max()]
    yaxis_l, yaxis_r = min(ycols), max(ycols)
    xrows = [r for r in range(h) if rs[r] > 0.8 * rs.max()]
    xaxis_t, xaxis_b = min(xrows), max(xrows)
    x_axis_row = 0.5 * (xaxis_t + xaxis_b)

    # y ticks: dark pixels just left of the axis line (a short band, clear of the labels)
    band = dark[:, yaxis_l - 12: yaxis_l - 2].all(axis=1)
    yt = [0.5 * (a + b) for a, b in _runs(band) if b - a < 20]
    yt = [t for t in yt if t <= xaxis_b + 2]
    if abs(yt[-1] - x_axis_row) > 6:  # the zero tick is on the x axis line
        yt.append(x_axis_row)
    yt = sorted(yt)
    yt = yt[-11:]
    yvals = [5.0 * (len(yt) - 1 - i) for i in range(len(yt))]
    ay, by, rms_y = _fit(yt, yvals)

    # x ticks: dark pixels just below the axis line
    band = dark[xaxis_b + 3: xaxis_b + 12, :].all(axis=0)
    xt = [0.5 * (a + b) for a, b in _runs(band) if b - a < 20]
    xt = sorted(xt)[-11:]
    xvals = [20.0 * i for i in range(len(xt))]
    ax, bx, rms_x = _fit(xt, xvals)

    out = []
    for x in at:
        col = int(round((x - bx) / ax))
        colv = dark[: xaxis_t - 2, col]
        runs = [(a, b) for a, b in _runs(colv) if a > 5]
        if not runs:
            out.append({"x": x, "y": None, "note": "no bar outline found in the bin's centre column"})
            continue
        a, b = runs[0]
        # the run must be an outline above a grey fill
        below = gray[b + 3: b + 20, col]
        if not (110 < below.mean() < 200):
            out.append({"x": x, "y": None, "note": "dark run without grey fill below; not a bar top"})
            continue
        row = 0.5 * (a + b)
        y = ay * row + by
        half = 0.5 * (b - a + 1) * abs(ay) + 2 * rms_y + 0.5 * abs(ay)
        out.append({"x": x, "y": float(y), "lo": float(y - half), "hi": float(y + half),
                    "px": [col, row], "px_lo": float(row + half / abs(ay)), "px_hi": float(row - half / abs(ay)),
                    "note": f"outline rows {a}-{b}; y calibration {len(yt)} ticks, rms {rms_y:.3f}; "
                            f"x calibration {len(xt)} ticks, rms {rms_x:.3f} um"})
    return out
