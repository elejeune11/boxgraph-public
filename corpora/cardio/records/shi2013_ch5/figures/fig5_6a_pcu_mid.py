"""Fig. 5-6(a) (p. 11): Pcu, the fine dotted line near 0 mmHg, read where it runs between Ps
(the dash-dot line, below it) and Pct/Pcl (above it): the second-lowest run of ink of the plot.
Calibration as in fig5_6a_pcu.py (see _common.py); the legend is left out.

Over the columns within `WINDOW` px either side of x, each column holding at least three runs of
ink gives its second-lowest run; a dash or dot of Ps or Pcu may miss a column, so the median row of
those runs is taken as the curve, and only runs within 15 px of it are kept. The value is the
centre of the kept run closest to x; it is refused when fewer than a third of the window's columns
agree, or when the run below or above it lies within `CLEAR` px (curves not apart). The interval
adds half the run, one raster pixel, the calibration misfits and the spread of the kept rows."""
import importlib.util
import os

import numpy as np

_spec = importlib.util.spec_from_file_location("_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)

LEGEND = (1580, 60, 2300, 480)
WINDOW = 12
CLEAR = 25


def read(image, at):
    cal = _c.calibrate(image, [-80, -40, 0, 40, 80, 120, 160], [36, 36.5, 37], -120, None)
    m = _c.interior(cal, LEGEND)
    out = []
    for x in at:
        x = float(x)
        c = int(round(_c.to_col(cal, x)))
        cands = []
        for k in range(max(c - WINDOW, 0), min(c + WINDOW + 1, m.shape[1])):
            rr = _c._runs(m[:, k])
            if len(rr) < 3:
                continue
            a, b = rr[-2]
            below, above = rr[-1], rr[-3]
            cands.append((k, a, b, below, above))
        n = 2 * WINDOW + 1
        if not cands:
            out.append({"x": x, "y": None, "note": "no column with three curves"})
            continue
        med = float(np.median([(a + b - 1) / 2.0 for _, a, b, _, _ in cands]))
        kept = [q for q in cands if abs((q[1] + q[2] - 1) / 2.0 - med) <= 15]
        if len(kept) < n / 3:
            out.append({"x": x, "y": None, "note": f"only {len(kept)} of {n} columns agree"})
            continue
        k, a, b, below, above = min(kept, key=lambda q: abs(q[0] - c))
        gap = min(below[0] - b, a - above[1])
        if gap < CLEAR:
            out.append({"x": x, "y": None, "note": f"neighbouring curve {gap} px away: not apart"})
            continue
        row = (a + b - 1) / 2.0
        rows = [(q[1] + q[2] - 1) / 2.0 for q in kept]
        spread = (max(rows) - min(rows)) / 2.0
        e = (b - a) / 2.0 + _c.BLUR + cal["ymis"] + spread
        out.append({"x": x, "y": _c.yval(cal, row), "lo": _c.yval(cal, row + e), "hi": _c.yval(cal, row - e),
                    "px": [float(k), float(row)], "px_lo": row - e, "px_hi": row + e,
                    "note": f"second-lowest ink, {len(kept)} of {n} columns agree, column {k - c:+d} px, run {b - a} px"})
    return out
