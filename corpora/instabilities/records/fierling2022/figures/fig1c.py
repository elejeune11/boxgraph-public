"""Fig. 1c (PDF p. 4): mean curvature of the ventral tissue (black horizontal line) and its error bar
(mean +- standard deviation, n = 4 embryos) at the phases t0, t1, t2, t3 of the ablation experiment.
x is the phase index: t0 = 0, t1 = 1, t2 = 2, t3 = 3.

Calibration from the image (a GraphPad-style plot: an open left axis with outward ticks, no frame):
- the y axis is the column with the longest dark vertical run in the left third; its ticks are dark
  runs reaching at least 15 px to the left of it; they are matched top to bottom to the printed
  0.02, 0.00, -0.02, -0.04, -0.06, -0.08 (the last on the x axis line) and fitted linearly;
- the x axis is the row with the longest dark horizontal run; its ticks are dark runs reaching at
  least 15 px below it, matched left to right to t0, t1, t2, t3.
Each bar: the column through the phase's tick; the bar is the longest dark vertical run in that column
inside the plot (the significance lines above 0.015 are left out). The mean is the row band of the
longest dark horizontal run centred on that column within the bar's rows; the caps are the topmost
and bottommost centred runs a third to two thirds as long. A value is the middle of its stroke.
95% interval: 2 px plus the calibration misfit; bar ends widened by 3 px plus the misfit.
The red dots (one per embryo) are not read here: they overlap the bars and caps.
"""
import numpy as np

YLAB = [0.02, 0.0, -0.02, -0.04, -0.06, -0.08]


def _runs(v):
    idx = np.where(v)[0]
    if len(idx) == 0:
        return []
    out, s, p = [], idx[0], idx[0]
    for i in idx[1:]:
        if i != p + 1:
            out.append((s, p))
            s = i
        p = i
    out.append((s, p))
    return out


def _groups(idx, gap=3):
    out = []
    for i in idx:
        if out and i - out[-1][-1] <= gap:
            out[-1].append(i)
        else:
            out.append([i])
    return out


def _run_through(v, i):
    if not v[i]:
        return None
    a = i
    while a > 0 and v[a - 1]:
        a -= 1
    b = i
    while b < len(v) - 1 and v[b + 1]:
        b += 1
    return a, b


def read(image, at):
    f = image.astype(float)
    blk = (f.mean(axis=2) < 100) & ((f.max(axis=2) - f.min(axis=2)) < 60)
    H, W = blk.shape
    # y axis: longest vertical run in the left third
    best = (0, 0, None)
    for c in range(W // 3):
        for a, b in _runs(blk[:, c]):
            if b - a > best[0]:
                best = (b - a, c, (a, b))
    cols = [c for c in range(W // 3) if any(b - a > 0.9 * best[0] for a, b in _runs(blk[:, c]))]
    ax_c0, ax_c1 = min(cols), max(cols)
    top, bot = best[2]
    # x axis: longest horizontal run
    bestx = (0, 0)
    for r in range(H):
        for a, b in _runs(blk[r]):
            if b - a > bestx[0]:
                bestx = (b - a, r)
    rows_x = [r for r in range(H) if any(b - a > 0.9 * bestx[0] for a, b in _runs(blk[r]))]
    xr0, xr1 = min(rows_x), max(rows_x)
    # y ticks: dark pixels 15 px left of the axis
    tick_rows = [r for r in range(top, bot + 1) if blk[r, ax_c0 - 15:ax_c0].all()]
    ty = [float(np.mean(g)) for g in _groups(tick_rows)]
    if len(ty) != len(YLAB):
        raise ValueError(f"found {len(ty)} y ticks, expected {len(YLAB)}")
    by, ay = np.polyfit(ty, YLAB, 1)
    my = float(np.max(np.abs(np.array(ty) - (np.array(YLAB) - ay) / by)))
    # x ticks: dark pixels 15 px below the axis
    tick_cols = [c for c in range(ax_c1 + 5, W) if blk[xr1 + 1:xr1 + 16, c].all()]
    tx = [float(np.mean(g)) for g in _groups(tick_cols)]
    if len(tx) != 4:
        raise ValueError(f"found {len(tx)} x ticks, expected 4")
    to_v = lambda r: float(ay + by * r)  # noqa: E731
    r_hi = int((0.015 - ay) / by)  # rows below the value 0.015
    out = []
    for x in at:
        k = int(round(float(x)))
        c = int(round(tx[k]))
        col = blk[:, c].copy()
        col[:r_hi] = False
        col[xr0 - 3:] = False
        runs = _runs(col)
        a, b = max(runs, key=lambda q: q[1] - q[0])
        cand = []
        for r in range(a - 10, b + 11):
            q = _run_through(blk[r], c)
            if q and abs((q[0] + q[1]) / 2.0 - c) < 15:
                cand.append((r, q[1] - q[0] + 1))
        L = max(n for _, n in cand)
        mean_rows = [r for r, n in cand if n >= 0.8 * L]
        g_mean = max(_groups(mean_rows), key=len)
        r_mean = (g_mean[0] + g_mean[-1]) / 2.0
        caps = [r for r, n in cand if 0.33 * L <= n <= 0.7 * L]
        gcaps = _groups(caps)
        e = 2.0 + max(my, 0.5)
        rec = {"x": float(x), "y": to_v(r_mean), "px": [float(c), r_mean],
               "note": f"mean line rows {g_mean[0]}-{g_mean[-1]} ({L} px long); y {len(ty)} ticks misfit {my:.2f} px"}
        rec["lo"], rec["hi"] = sorted([to_v(r_mean + e), to_v(r_mean - e)])
        if len(gcaps) >= 2:
            ct, cb = gcaps[0], gcaps[-1]
            rt, rb = (ct[0] + ct[-1]) / 2.0, (cb[0] + cb[-1]) / 2.0
            eb = 3.0 + max(my, 0.5)
            rec.update({"bar_hi": to_v(rt), "bar_lo": to_v(rb), "bar_hi_outer": to_v(rt - eb),
                        "bar_lo_outer": to_v(rb + eb), "px_lo": rt, "px_hi": rb})
            rec["note"] += f"; caps at rows {ct[0]}-{ct[-1]} and {cb[0]}-{cb[-1]}"
        else:
            rec["note"] += "; caps not told apart from the mean line"
        out.append(rec)
    return out
