"""Read the single blue curve of Fig. 3 (U / mu L^2 against applied strain epsilon).

The axes are calibrated from the tick marks of the plot frame: nine x ticks labelled
0.2, 0.22, ..., 0.36 and nine y ticks labelled 0, 0.1, ..., 0.8.
"""
import numpy as np

X_LABELS = [0.20, 0.22, 0.24, 0.26, 0.28, 0.30, 0.32, 0.34, 0.36]
Y_LABELS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]


def _runs(mask_1d):
    """Centres of consecutive True runs."""
    idx = np.flatnonzero(mask_1d)
    if idx.size == 0:
        return []
    groups = np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1)
    return [float(g.mean()) for g in groups]


def _frame(dark):
    """Rows and columns of the frame lines: the longest dark lines."""
    rows = dark.sum(axis=1)
    cols = dark.sum(axis=0)
    long_rows = np.flatnonzero(rows > 0.6 * dark.shape[1])
    long_cols = np.flatnonzero(cols > 0.6 * dark.shape[0])
    return long_rows.min(), long_rows.max(), long_cols.min(), long_cols.max()


def _fit(px, labels):
    a, b = np.polyfit(px, labels, 1)
    resid = np.asarray(labels) - (a * np.asarray(px) + b)
    return a, b, float(np.max(np.abs(resid)))


def read(image, at):
    img = image.astype(float)
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    dark = (r < 100) & (g < 100) & (b < 100)
    top, bottom, left, right = _frame(dark)

    # x ticks: short dark vertical marks just above the bottom frame line, inside the box
    band = dark[bottom - 25:bottom - 6, left + 4:right - 3]
    xt = [c + left + 4 for c in _runs(band.mean(axis=0) > 0.8)]
    xt = [left] + xt + [right]          # the first and last labels sit on the frame corners
    # y ticks: short dark horizontal marks just right of the left frame line
    band = dark[top + 4:bottom - 3, left + 6:left + 25]
    yt = [rr + top + 4 for rr in _runs(band.mean(axis=1) > 0.8)]
    yt = [bottom] + sorted(yt, reverse=True) + [top]
    if len(xt) != len(X_LABELS) or len(yt) != len(Y_LABELS):
        raise ValueError(f"found {len(xt)} x ticks and {len(yt)} y ticks")
    ax, bx, mx = _fit(xt, X_LABELS)
    ay, by, my = _fit(yt, Y_LABELS)

    blue = (b > 150) & (r < 120) & (g < 120) & (b - r > 80)
    out = []
    for x in at:
        col = (x - bx) / ax
        c = int(round(col))
        rows = np.flatnonzero(blue[top:bottom, max(c - 1, 0):c + 2].any(axis=1)) + top
        if rows.size == 0:
            out.append({"x": x, "y": None, "note": "no curve at this strain (the curve ends near 0.351)"})
            continue
        rc = float(rows.mean())
        y = ay * rc + by
        # 95% half-interval: half the curve's extent in this column, a 2 px floor, plus the calibration misfit
        half_px = max((rows.max() - rows.min()) / 2 + 2, 3)
        dy = abs(ay) * half_px + my
        # x calibration misfit shifts the column; convert through the local slope
        rows_l = np.flatnonzero(blue[top:bottom, max(c - 6, 0):c - 3].any(axis=1))
        rows_r = np.flatnonzero(blue[top:bottom, c + 4:c + 7].any(axis=1))
        if rows_l.size and rows_r.size:
            slope = abs(ay) * abs(rows_r.mean() - rows_l.mean()) / (abs(ax) * 9)  # dy/dx in axis units
            dy += slope * mx
        y, dy = float(y), float(dy)
        out.append({"x": x, "y": y, "lo": y - dy, "hi": y + dy, "px": [c, rc],
                    "px_lo": float(rc - half_px), "px_hi": float(rc + half_px),
                    "note": f"x misfit {mx:.2g}, y misfit {my:.2g}"})
    return out
