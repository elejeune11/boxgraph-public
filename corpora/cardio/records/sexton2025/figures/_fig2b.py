"""Fig. 2B (p. 3): theoretical clock cycles C (log) against bifurcation depth B for full balanced trees:
the red dotted line ("Naive Implementation, C ~ (N*E)^2") and the red dashed line ("Recompute Entire
Tree, C ~ N^2"). The blue partial-binding lines (one per number of local evaluations E, graded shades
of one blue) overlap and are not read.

Calibration: frame lines (dark < 110); y decade ticks are the long ticks out to the left (runs of at
least 25 px at 1000 dpi; minor ticks are shorter), matched to 10^9, 10^8, 10^7, 10^6 from the top; x ticks
out below matched to 10, 20, ..., 80 (the 0 tick merges with the y axis and is not used). Log fit on y.

Lines: both are straight in these axes (log C against B). The red mask (within 70 of (235, 30, 40)) is
split into connected pieces. Dashes are pieces longer than 40 px; dots are pieces 12-40 px across,
neither side more than twice the other. The red labels next to the lines are the same red; their
letters are pieces too, so the line is found by RANSAC: of every pair of candidate pieces, the straight
line through their centres that passes within 5 px of the most candidates; then a least-squares line
through those inliers. A reading at B is that line's row at B's column; interval: twice the inliers'
rms distance from the line + the line's half-width + the misfits. Readings are limited to the span
the inliers cover.
"""

import os
import sys

import numpy as np
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _curves as K  # noqa: E402
import _common as C  # noqa: E402

RED = (235, 30, 40)


def read(image, at, which):
    ax_x, ax_y, box = K.axes(image, [1e9, 1e8, 1e7, 1e6], [10, 20, 30, 40, 50, 60, 70, 80], yscale="log10",
                             dark=110, ylen=25, ymin=25, xlen=12)
    m = K.mask_of(image, RED, 70, box)
    lab, _ = ndimage.label(m)
    pts, halfw = [], []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        rr, cc = np.nonzero(lab[sl] == i + 1)
        if which == "dashed":
            ok = max(h, w) > 40 and len(rr) < 0.6 * h * w
        else:
            ok = 12 <= h <= 40 and 12 <= w <= 40 and max(h, w) <= 2 * min(h, w)
        if ok:
            pts.append((cc.mean() + sl[1].start + 0.5, rr.mean() + sl[0].start + 0.5))
            halfw.append(min(h, w) / 2.0 if which == "dotted" else 6.0)
    P = np.array(pts)
    best = None
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            (x1, y1), (x2, y2) = P[i], P[j]
            if abs(x2 - x1) < 50:
                continue
            s = (y2 - y1) / (x2 - x1)
            d = np.abs(P[:, 1] - (y1 + s * (P[:, 0] - x1))) / np.sqrt(1 + s * s)
            inl = d < 5
            if best is None or inl.sum() > best.sum():
                best = inl
    Q = P[best]
    b, a = np.polyfit(Q[:, 0], Q[:, 1], 1)
    rms = float(np.sqrt(np.mean((Q[:, 1] - (a + b * Q[:, 0])) ** 2)))
    lw = float(np.median(np.array(halfw)[best]))
    x0, x1 = Q[:, 0].min(), Q[:, 0].max()
    out = []
    for xv in at:
        x = float(xv)
        pc = ax_x.pix(x)
        if not (x0 - 20 <= pc <= x1 + 20):
            out.append({"x": x, "y": None, "note": "outside the span the line's pieces cover"})
            continue
        row = a + b * pc
        h = 2 * rms + lw + abs(b) * ax_x.misfit + ax_y.misfit
        lo, hi = sorted((ax_y.val(row + h), ax_y.val(row - h)))
        out.append({"x": x, "y": ax_y.val(row), "lo": lo, "hi": hi, "px": [pc, row], "px_lo": row + h, "px_hi": row - h,
                    "note": f"line through {int(best.sum())} of {len(P)} candidate pieces; rms {rms:.2f} px"})
    return out


_ = C
