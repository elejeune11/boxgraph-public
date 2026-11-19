# Fig. 4 (PDF p. 6): phase diagram in the (l0, u) plane. Reads the l0 position of a vertical
# black boundary line at given u values. The axes are calibrated from the image: the tick marks
# under the l0 axis (labels 3, 3.5, ..., 6) and left of the u axis (labels 1, 0, -1).
# Reading convention: x is u (the position along the line), y is the l0 of the line there.
import numpy as np
from scipy import ndimage

L0_LABELS = [3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]
U_LABELS = [1.0, 0.0, -1.0]


def _black(image):
    im = image[..., :3].astype(float) / 255
    return (im.max(-1) < 0.3) & (im.max(-1) - im.min(-1) < 0.2)


def _runs(v):
    """(start, end) of runs of True in a 1-D boolean array (end exclusive)."""
    d = np.diff(np.r_[0, v.astype(int), 0])
    return list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)))


def calibrate(image):
    blk = _black(image)
    h, w = blk.shape
    # l0 axis: the row with the longest black run, in the lower half
    rows = [max((e - s for s, e in _runs(blk[r])), default=0) for r in range(h)]
    lower = range(h // 2, h)
    ax_row = max(lower, key=lambda r: rows[r])
    ax_rows = [r for r in lower if rows[r] > 0.8 * rows[ax_row]]
    r_top, r_bot = min(ax_rows), max(ax_rows)
    # u axis: the column with the longest black run, in the left fifth
    cols = [max((e - s for s, e in _runs(blk[:, c])), default=0) for c in range(w // 5)]
    ax_col = int(np.argmax(cols))
    ax_cols = [c for c in range(w // 5) if cols[c] > 0.8 * cols[ax_col]]
    c_l, c_r = min(ax_cols), max(ax_cols)
    # x ticks: black columns in a band just below the axis line, right of the u axis
    band = blk[r_bot + 8:r_bot + 40, c_r + 20:]
    tick_cols = [(s + e - 1) / 2 + c_r + 20 for s, e in _runs(band.mean(0) > 0.8)]
    if len(tick_cols) != len(L0_LABELS):
        raise ValueError(f"found {len(tick_cols)} l0 ticks, expected {len(L0_LABELS)}")
    # u ticks: black rows in a band just left of the u axis, above the l0 axis
    band = blk[:r_top - 20, max(c_l - 40, 0):c_l - 8]
    tick_rows = [(s + e - 1) / 2 for s, e in _runs(band.mean(1) > 0.8)]
    if len(tick_rows) != len(U_LABELS):
        raise ValueError(f"found {len(tick_rows)} u ticks, expected {len(U_LABELS)}")
    fx = np.polyfit(tick_cols, L0_LABELS, 1)
    fy = np.polyfit(tick_rows, U_LABELS, 1)
    mis_x = float(np.max(np.abs(np.polyval(fx, tick_cols) - L0_LABELS)))
    mis_y = float(np.max(np.abs(np.polyval(fy, tick_rows) - U_LABELS)))
    return fx, fy, mis_x, mis_y


def read_line(image, at, l0_lo, l0_hi):
    """l0 of the vertical black line found between l0_lo and l0_hi, at each u in `at`."""
    blk = _black(image)
    fx, fy, mis_x, mis_y = calibrate(image)
    col_of = lambda l0: (l0 - fx[1]) / fx[0]
    row_of = lambda u: (u - fy[1]) / fy[0]
    c0, c1 = int(round(min(col_of(l0_lo), col_of(l0_hi)))), int(round(max(col_of(l0_lo), col_of(l0_hi))))
    out = []
    for u in at:
        r = int(round(row_of(u)))
        seg = blk[r - 3:r + 4, c0:c1].mean(0) > 0.99
        runs = [(s, e) for s, e in _runs(seg) if 3 <= e - s <= 20]
        if len(runs) != 1:
            out.append({"x": u, "y": None, "note": f"{len(runs)} candidate line segments in this row band"})
            continue
        s, e = runs[0]
        col = c0 + (s + e - 1) / 2
        l0 = float(np.polyval(fx, col))
        half = float((e - s) / 2 * abs(fx[0]))  # half the line width, in l0
        err = half + mis_x + float(abs(fx[0]))
        out.append({"x": u, "y": l0, "lo": l0 - err, "hi": l0 + err, "px": [float(col), r],
                    "note": f"line {e - s} px wide; l0 calibration misfit {mis_x:.4f}, u misfit {mis_y:.4f}"})
    return out


def line_extent(image, l0_lo, l0_hi):
    """u at the top and bottom ends of the black line, and gaps (for figures.md)."""
    blk = _black(image)
    fx, fy, *_ = calibrate(image)
    col_of = lambda l0: (l0 - fx[1]) / fx[0]
    c0, c1 = int(round(col_of(l0_lo))), int(round(col_of(l0_hi)))
    colsum = blk[:, c0:c1].sum(0)
    c = c0 + int(np.argmax(colsum))
    runs = [(s, e) for s, e in _runs(blk[:, c]) if e - s > 50]
    return [(float(np.polyval(fy, s)), float(np.polyval(fy, e - 1))) for s, e in runs]
