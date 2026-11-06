# Reads the driver curve e(t) of Fig. 3 (page 4). The plot has a frame, dotted grey
# gridlines at every labelled tick (x: 0.1 ... 0.5, y: 0.1 ... 0.9) and one blue curve.
# The frame's left edge is the x label 0, its bottom edge the y label 0 and its top edge
# the y label 1. Calibration: least-squares lines through the frame edges and the
# detected gridlines, matched in order to the printed labels.
import numpy as np


def _groups(idx):
    idx = np.asarray(idx)
    if idx.size == 0:
        return []
    return np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1)


def _longest_run(mask_2d, axis):
    """Longest contiguous run of True along `axis`, for each line across the other axis."""
    m = mask_2d if axis == 0 else mask_2d.T
    best = np.zeros(m.shape[1], dtype=int)
    cur = np.zeros(m.shape[1], dtype=int)
    for row in m:
        cur = np.where(row, cur + 1, 0)
        best = np.maximum(best, cur)
    return best


def read(image, at):
    img = image[:, :, :3].astype(float)
    r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    blue = (b > 120) & (b - r > 60) & (b - g > 40)
    ink = (np.minimum(np.minimum(r, g), b) < 235) & (np.abs(r - g) < 40) & (np.abs(g - b) < 40) & ~blue
    H, W = ink.shape

    # frame: lines whose longest continuous ink run is close to the longest of all
    col_run = _longest_run(ink, axis=0)
    row_run = _longest_run(ink, axis=1)
    fcols = [float(gp.mean()) for gp in _groups(np.flatnonzero(col_run > 0.6 * col_run.max()))]
    frows = [float(gp.mean()) for gp in _groups(np.flatnonzero(row_run > 0.6 * row_run.max()))]
    left, right = min(fcols), max(fcols)
    top, bottom = min(frows), max(frows)

    # dotted gridlines: interior lines with a large share of ink but no long run
    m = max(4, int(0.01 * (right - left)))
    t0, t1, l0, l1 = int(top) + m, int(bottom) - m, int(left) + m, int(right) - m
    inner = ink[t0:t1, l0:l1]
    cfrac = inner.mean(axis=0)
    rfrac = inner.mean(axis=1)
    vcols = [float(gp.mean()) + l0 for gp in _groups(np.flatnonzero(cfrac > 0.2))]
    hrows = [float(gp.mean()) + t0 for gp in _groups(np.flatnonzero(rfrac > 0.2))]

    xs_px = [left] + vcols
    xs_val = [0.1 * i for i in range(len(xs_px))]
    ax, bx = np.polyfit(xs_px, xs_val, 1)
    x_mis = float(np.max(np.abs(np.polyval([ax, bx], xs_px) - xs_val)))
    ys_px = [bottom] + sorted(hrows, reverse=True) + [top]
    ys_val = [0.1 * i for i in range(len(ys_px))]
    ay, by = np.polyfit(ys_px, ys_val, 1)
    y_mis = float(np.max(np.abs(np.polyval([ay, by], ys_px) - ys_val)))
    calib_ok = len(vcols) == 5 and len(hrows) == 9
    note0 = (f"calibration: frame cols {left:.0f}-{right:.0f}, rows {top:.0f}-{bottom:.0f}; "
             f"{len(vcols)} x gridlines, {len(hrows)} y gridlines; misfit x {x_mis:.4f}, y {y_mis:.4f}")
    if not calib_ok:
        return [{"x": x, "y": None, "note": note0 + "; gridline count differs from the printed ticks, not read"}
                for x in at]

    out = []
    k = 1 + int(np.ceil(x_mis / abs(ax)))   # columns within the x misfit either side
    for x in at:
        ci = int(round((x - bx) / ax))
        if ci - k < 0 or ci + k >= W:
            out.append({"x": x, "y": None, "note": "outside the crop"})
            continue
        rows = np.flatnonzero(blue[:, ci - k:ci + k + 1].any(axis=1))
        if rows.size == 0:
            out.append({"x": x, "y": None, "note": "no blue curve pixels in this column"})
            continue
        lo_r, hi_r = int(rows.min()), int(rows.max())
        mid = 0.5 * (lo_r + hi_r)
        y = float(np.polyval([ay, by], mid))
        # interval: the curve's vertical extent over those columns (line thickness and
        # slope over the x misfit), half a pixel each side, and the y calibration misfit
        ya = float(np.polyval([ay, by], lo_r - 0.5))
        yb = float(np.polyval([ay, by], hi_r + 0.5))
        out.append({"x": x, "y": y, "lo": min(ya, yb) - y_mis, "hi": max(ya, yb) + y_mis,
                    "px": [ci, mid], "px_lo": float(lo_r), "px_hi": float(hi_r), "note": note0})
    return out
