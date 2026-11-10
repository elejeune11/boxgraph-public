"""Fig. S8 (p. 51): build time (s, log) against tree size (log) for 100, 1000, 4000 and 8000 terminals;
one line per tissue domain with +-1 SD error bars (100 trees each). Blue lines (non-convex domains, 208
anatomic and engineered ones) overlap into one band and are not read; the two dark red lines (convex
domains) are read: the upper and the lower one.

Calibration: frame lines (dark < 100); the decade ticks are the long ones (runs of at least 22 px at
1000 dpi; minor ticks are shorter): y 10^3, 10^2, 10^1 from the top, x 10^2, 10^3 (the 10^4 decade is past
the plot's right edge). Log fits on both axes; misfit widens intervals.

Reading a red line at a tree size N: the dark red mask (R > 80, R > 2.2 G, R > 2.2 B; the blue lines
and grey grid are excluded) is traced (see _curves.py) from x = 2000, where the two red lines are
apart and carry no error bar; 'upper' is the higher red run there, 'lower' the lower. At the data
columns the error bar and marker merge with the line, so the line's height there is taken from the
straight (log-log) segments on either side: the trace's centres 30-60 px left and right of N (only the
left side at 8000, the last point), extrapolated to N's column and averaged; interval: their
disagreement, the line half-width and the misfits. The error bar: the extent of the red run in N's
column (+-3 px, the stem), with its two caps as ends; not read where that run also holds the other red
line (at N = 100 the two lines' bars overlap).
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

from boxgraph import digitize as D  # noqa: E402


def calibrate(image):
    rows, cols = C.frame(image, 100, 0.45)
    yc, xr = cols[0], rows[-1]
    yt = [t[0] for t in C.ticks_on_vertical(image, yc[1], yc[2], "out", 25, 0, xr[2] + 15, 100, 22)]
    xt = [t[0] for t in C.ticks_on_horizontal(image, xr[1], xr[2], "out", 25, yc[2] + 5, image.shape[1], 100, 22)]
    if len(yt) != 3 or len(xt) != 2:
        raise RuntimeError(f"expected 3 y and 2 x decade ticks, found {yt} {xt}")
    ax_y = C.Axis(yt, [1e3, 1e2, 1e1], "log10")
    ax_x = C.Axis(xt, [1e2, 1e3], "log10")
    return ax_x, ax_y, (yc[2] + 2, rows[0][2] + 2, cols[-1][1] - 2, xr[1] - 2)


def red_mask(image, box):
    im = image[..., :3].astype(int)
    R, G, B = im[..., 0], im[..., 1], im[..., 2]
    m = (R > 80) & (R > 2.2 * G) & (R > 2.2 * B)
    out = np.zeros_like(m)
    c0, r0, c1, r1 = box
    out[r0:r1, c0:c1] = m[r0:r1, c0:c1]
    return out


def read(image, at, which, bars=True):
    other = {r["x"]: r["px"][1] for r in read(image, at, "lower" if which == "upper" else "upper", bars=False)
             if r["y"] is not None} if bars else {}
    ax_x, ax_y, box = calibrate(image)
    m = red_mask(image, box)
    sc = int(ax_x.pix(2000))
    runs = C.column_runs(m, sc)
    if len(runs) < 2:
        raise RuntimeError(f"expected two red lines at x = 2000, found {runs}")
    s, e = (min if which == "upper" else max)(runs, key=lambda t: t[0])
    path = D.trace(m, (sc + 0.5, (s + e) / 2.0), max_gap=40)
    halves = [h for (_, h, amb) in path.values() if not amb]
    lw = float(np.median(halves))
    out = []
    for xv in at:
        x = float(xv)
        pc = ax_x.pix(x)
        c = int(pc)
        est = []
        for side in (-1, 1):
            pts = [(cc, path[cc][0]) for cc in range(c + side * 30, c + side * 61, side)
                   if cc in path and not path[cc][2] and path[cc][1] < 2.5 * lw + 1]
            if len(pts) >= 5:
                xs, ys = np.array(pts, float).T
                b, a = np.polyfit(xs, ys, 1)
                est.append(a + b * pc)
        if not est:
            out.append({"x": x, "y": None, "note": "the line was not traced on either side of this point"})
            continue
        row = float(np.mean(est))
        dis = (max(est) - min(est)) / 2.0 if len(est) > 1 else 3.0
        h = dis + lw + 0.5 + ax_y.misfit
        lo, hi = sorted((ax_y.val(row - h), ax_y.val(row + h)))
        rec = {"x": x, "y": ax_y.val(row), "lo": lo, "hi": hi, "px": [pc, row],
               "note": f"line height from {len(est)} side(s); misfits x {ax_x.misfit:.2f}, y {ax_y.misfit:.2f} px"}
        if not bars:
            out.append(rec)
            continue
        # the error bar: the red run through the line's row in this column (+-3)
        best = None
        for dc in range(-3, 4):
            for s2, e2 in C.column_runs(m, c + dc):
                if s2 - 2 <= row <= e2 + 2 and (best is None or e2 - s2 > best[1] - best[0]):
                    best = (s2, e2)
        if best and x in other and best[0] - 2 <= other[x] <= best[1] + 2:
            rec["note"] += "; its error bar overlaps the other red line's: not read"
        elif best and best[1] - best[0] > 2 * lw + 6:
            top_r, bot_r = best[0] + 0.5 * lw, best[1] - 0.5 * lw
            rec.update({"bar_hi": ax_y.val(top_r), "bar_lo": ax_y.val(bot_r),
                        "bar_hi_outer": ax_y.val(top_r - lw - ax_y.misfit), "bar_lo_outer": ax_y.val(bot_r + lw + ax_y.misfit),
                        "px_lo": bot_r, "px_hi": top_r})
            rec["note"] += f"; error bar rows {best[0]}-{best[1]} (caps at the ends)"
        else:
            rec["note"] += "; no error bar wider than the marker"
        out.append(rec)
    return out
