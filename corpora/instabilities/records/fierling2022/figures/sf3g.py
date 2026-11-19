"""Supp. Fig. 3g (PDF p. 25): mean inward movement of the anterior pole (thick black horizontal line)
and its error bar (mean +- standard deviation, n = 5 embryos). One category; x = 0.

Calibration from the image (a GraphPad-style plot, as Fig. 1c, helpers in fig1c.py): the y axis is
the column with the longest dark vertical run in the left half; its outward ticks (dark runs reaching
15 px left of it) are matched top to bottom to the printed 8, 6, 4, 2, 0 and fitted linearly.
The bar: the longest dark vertical run right of the axis that is no wider than 20 px; the mean is the
row band of the longest dark horizontal run centred on the bar's column; the caps are the topmost and
bottommost centred runs a third to seven tenths as long. The black dots (one per embryo) lie on the
bar too but give much shorter runs. 95% interval: 2 px plus the misfit; bar ends 3 px plus the misfit.
"""
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the helpers beside this file
from fig1c import _groups, _run_through, _runs  # noqa: E402

YLAB = [8.0, 6.0, 4.0, 2.0, 0.0]


def read(image, at):
    f = image.astype(float)
    blk = (f.mean(axis=2) < 100) & ((f.max(axis=2) - f.min(axis=2)) < 60)
    H, W = blk.shape
    best = (0, 0, None)
    for c in range(W // 2):
        for a, b in _runs(blk[:, c]):
            if b - a > best[0]:
                best = (b - a, c, (a, b))
    cols = [c for c in range(W // 2) if any(b - a > 0.9 * best[0] for a, b in _runs(blk[:, c]))]
    ax0, ax1 = min(cols), max(cols)
    top, bot = best[2]
    tick_rows = [r for r in range(top, bot + 1) if blk[r, ax0 - 15:ax0].all()]
    ty = [float(np.mean(g)) for g in _groups(tick_rows)]
    if len(ty) != len(YLAB):
        raise ValueError(f"found {len(ty)} y ticks, expected {len(YLAB)}")
    by, ay = np.polyfit(ty, YLAB, 1)
    my = float(np.max(np.abs(np.array(ty) - (np.array(YLAB) - ay) / by)))
    to_v = lambda r: float(ay + by * r)  # noqa: E731
    # the bar's column: the longest vertical run right of the axis, above the x axis line
    xr = int(round((0.0 - ay) / by))
    bestc = (0, None)
    for c in range(ax1 + 20, W):
        for a, b in _runs(blk[top:xr - 10, c]):
            if b - a > bestc[0]:
                bestc = (b - a, c)
    c = bestc[1]
    runs = _runs(blk[top:xr - 10, c])
    a, b = max(runs, key=lambda q: q[1] - q[0])
    a, b = a + top, b + top
    cand = []
    for r in range(a - 10, b + 11):
        q = _run_through(blk[r], c)
        if q and abs((q[0] + q[1]) / 2.0 - c) < 15:
            cand.append((r, q[1] - q[0] + 1))
    L = max(n for _, n in cand)
    g = max(_groups([r for r, n in cand if n >= 0.8 * L]), key=len)
    rm = (g[0] + g[-1]) / 2.0
    caps = _groups([r for r, n in cand if 0.33 * L <= n <= 0.7 * L])
    e, eb = 2.0 + max(my, 0.5), 3.0 + max(my, 0.5)
    lo, hi = sorted([to_v(rm + e), to_v(rm - e)])
    rec = {"x": 0.0, "y": to_v(rm), "lo": lo, "hi": hi, "px": [float(c), rm],
           "note": f"mean line rows {g[0]}-{g[-1]} ({L} px long); y {len(ty)} ticks misfit {my:.2f} px"}
    if len(caps) >= 2:
        rt = (caps[0][0] + caps[0][-1]) / 2.0
        rb = (caps[-1][0] + caps[-1][-1]) / 2.0
        rec.update({"bar_hi": to_v(rt), "bar_lo": to_v(rb), "bar_hi_outer": to_v(rt - eb),
                    "bar_lo_outer": to_v(rb + eb), "px_lo": rt, "px_hi": rb})
        rec["note"] += f"; caps at rows {caps[0][0]}-{caps[0][-1]} and {caps[-1][0]}-{caps[-1][-1]}"
    return [rec for x in at if float(x) == 0.0]
