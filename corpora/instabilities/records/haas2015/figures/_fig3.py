"""Shared reading code for Fig. 3(g) and 3(h) (PDF p. 4): black curves on linear axes.

Calibration, all from the image:
- dark = grey level below 170 (antialiased black lines).
- the y axis is the darkest long column in the left third; the x axis is the darkest long row
  below the top fifth (in panel (h) it is the line y = 0 inside the plot).
- x ticks: short dark runs crossing the x axis row (dark both just above and just below it).
  On the figure the labels 5, 10 (and 15) sit on every third tick counted from the y axis
  (lambda/delta = 0, labelled 0 in panel (g)), so the ticks are 5/3 apart; runs off that
  regular grid (a curve or a dashed line crossing the axis) are dropped. The x scale is the
  least-squares line through the ticks at their values; its residual is the x misfit.
- y ticks: short dark runs crossing the y axis column, regular in spacing. Ticks with digits to
  their left are the labelled ones; their values are given by the caller in order from the top
  (those printed on the figure). The y scale is fitted through the labelled ticks and checked on
  the unlabelled ones (the misfit enters the interval).
Curves: in each column within +-3 px of the reading position, the dark runs between the top of
the plot and the bottom of the crop, excluding the axes' rows and columns, are taken; the run
chosen by the caller's selector gives the curve's centre row. Value = median over the columns;
interval = half the run thickness (in y units) + y misfit + the change of the curve over the
x misfit.
"""
import numpy as np


def groups(idx, gap=1):
    out = []
    for c in idx:
        if out and c - out[-1][-1] <= gap:
            out[-1].append(int(c))
        else:
            out.append([int(c)])
    return out


def dark_mask(image):
    img = image.astype(float)
    gray = img.mean(axis=2) if img.ndim == 3 else img
    return gray < 170


def find_axes(dk):
    H, W = dk.shape
    colsum = dk.sum(0)
    c_axis = int(np.argmax(colsum[: W // 3]))
    rowsum = dk.sum(1)
    r_axis = int(H // 5 + np.argmax(rowsum[H // 5:]))
    # line width: thickness of the x axis run at 60% of the width
    c_mid = int(c_axis + 0.6 * (W - c_axis))
    run = [g for g in groups(np.where(dk[:, c_mid])[0]) if g[0] - 2 <= r_axis <= g[-1] + 2]
    lw = max(2, len(run[0]) if run else 2)
    return c_axis, r_axis, lw


def regular(ticks, origin=None):
    """Keep the ticks on one regular grid; returns (kept ticks, spacing)."""
    t = np.array(sorted(ticks))
    d = np.diff(t)
    # spacing: the commonest gap (gaps within 10% of each other), then refined by a fit
    sp = float(max(d, key=lambda g: int(np.sum(np.abs(d - g) < 0.1 * g))))
    if origin is not None:
        ref = origin
    else:  # the tick that puts the most others on its grid
        ref = max(t, key=lambda r: int(np.sum(np.abs((t - r) / sp - np.round((t - r) / sp)) < 0.15)))
    for _ in range(3):
        k = (t - ref) / sp
        keep = np.abs(k - np.round(k)) < 0.15
        kk = np.round(k[keep])
        if keep.sum() >= 2 and np.ptp(kk) > 0:
            A = np.vstack([np.ones_like(kk), kk]).T
            (r0, sp), *_ = np.linalg.lstsq(A, t[keep], rcond=None)
            if origin is None:
                ref = r0
    k = (t - ref) / sp
    keep = np.abs(k - np.round(k)) < 0.15
    return list(t[keep]), float(sp)


def x_ticks(dk, c_axis, r_axis, lw):
    a, b = int(0.6 * lw) + 1, int(1.4 * lw) + 1
    below = dk[r_axis + a: r_axis + b, :].mean(0)
    above = dk[max(r_axis - b, 0): r_axis - a, :].mean(0)
    found = []
    for mask in ((below > 0.5) & (above > 0.5), below > 0.5, above > 0.5):
        cols = np.where(mask)[0]
        cols = cols[cols > c_axis + 2 * lw]
        for g in groups(cols):
            if len(g) <= 3 * lw:
                c = float(np.mean(g))
                if all(abs(c - f) > lw for f in found):
                    found.append(c)
    return sorted(found)


def y_ticks(dk, c_axis, r_axis, lw, r_top, below_axis=False):
    a, b = int(0.6 * lw) + 1, int(1.4 * lw) + 1
    left = dk[:, max(c_axis - b, 0): c_axis - a].mean(1)
    right = dk[:, c_axis + a: c_axis + b].mean(1)
    rows = np.where((left > 0.5) & (right > 0.5))[0]
    rows = rows[rows > r_top]
    if not below_axis:  # panel (g): below its x axis is only the axis break
        rows = rows[rows < r_axis + 2 * lw]
    return [float(np.mean(g)) for g in groups(rows) if len(g) <= 3 * lw]


def calibrate(image, y_labels, x_per_tick, below_axis=False):
    """y_labels: printed values of the labelled y ticks, from the top down.
    x_per_tick: the x step between neighbouring ticks, as matched to the labels seen on the figure
    (the y axis column is 0 and the labels 5, 10, 15 sit on every third tick: 5/3 per tick)."""
    dk = dark_mask(image)
    H, W = dk.shape
    c_axis, r_axis, lw = find_axes(dk)
    # top of the y axis (arrow tip): first dark row of the axis column
    axcol = np.where(dk[:, c_axis])[0]
    r_top = int(axcol.min()) + 2 * lw
    xt, xsp = regular(x_ticks(dk, c_axis, r_axis, lw), origin=c_axis)
    xi = np.round((np.array(xt) - c_axis) / xsp) * x_per_tick
    A = np.vstack([np.ones_like(xi), xi]).T
    sol, *_ = np.linalg.lstsq(np.vstack([A, [1, 0]]), np.concatenate([np.array(xt), [c_axis]]), rcond=None)
    c0, cpu = sol  # column of x = 0, columns per unit
    xmis = float(np.max(np.abs(c0 + cpu * xi - np.array(xt))) / cpu) if len(xt) else 0.0
    yt_all = y_ticks(dk, c_axis, r_axis, lw, r_top, below_axis)
    yt, ysp = regular(yt_all)
    lab = []
    for t in yt:
        # digits just left of the tick (the rotated axis title lies further left)
        win = dk[int(t - ysp / 3): int(t + ysp / 3), max(c_axis - int(1.0 * ysp), 0): max(c_axis - 2 * lw, 1)]
        if win.sum() > 6 * lw * lw:
            lab.append(t)
    assert len(lab) == len(y_labels), (lab, yt)
    v = np.array(y_labels, dtype=float)
    p = np.array(lab)
    B = np.vstack([np.ones_like(p), p]).T
    (a, b), *_ = np.linalg.lstsq(B, v, rcond=None)
    # check all ticks on the grid of the labelled spacing
    step = abs(b) * ysp
    resid = []
    for t in yt:
        val = a + b * t
        k = (val - v[0]) / step
        resid.append(abs(k - round(k)) * step)
    ymis = float(max(resid)) if resid else 0.0
    return dict(dk=dk, c_axis=c_axis, r_axis=r_axis, lw=lw, r_top=r_top, c0=c0, cpu=cpu, xmis=xmis,
                a=a, b=b, ymis=ymis, below_axis=below_axis, ysp=ysp, nxt=len(xt), nyt=len(yt))


def runs_in_column(cal, c, exclude_axis=True):
    dk = cal["dk"]
    lw = cal["lw"]
    col = dk[:, c].copy()
    col[: cal["r_top"]] = False
    if not cal["below_axis"]:  # panel (g): below the x axis are only tick labels
        col[cal["r_axis"]:] = False
    if exclude_axis:
        col[cal["r_axis"] - lw: cal["r_axis"] + lw + 1] = False
    return [(g[0], g[-1]) for g in groups(np.where(col)[0])]


def read_at(image, at, y_labels, select, slope_fn=None, what="", half=3, x_per_tick=5.0 / 3.0, below_axis=False):
    cal = calibrate(image, y_labels, x_per_tick, below_axis)
    out = []
    for x in at:
        col = cal["c0"] + cal["cpu"] * x
        ci = int(round(col))
        rows, thick = [], []
        for c in range(ci - half, ci + half + 1):
            runs = runs_in_column(cal, c)
            r = select(runs, cal)
            if r is not None:
                rows.append((r[0] + r[1]) / 2)
                thick.append(r[1] - r[0] + 1)
        if len(rows) < 4:
            out.append({"x": float(x), "y": None, "note": f"{what}: no clear run here"})
            continue
        rows = np.array(rows)
        row = float(np.median(rows))
        near = np.abs(rows - row) <= 2 * cal["lw"]   # columns where the selector caught something else are dropped
        rows = rows[near]
        th = np.array(thick)[near]
        row = float(np.median(rows))
        y = cal["a"] + cal["b"] * row
        dy = abs(cal["b"]) * (float(np.median(th)) / 2 + float(np.ptp(rows)) / 2) + cal["ymis"]
        # the curve's local slope times the x misfit
        dc = max(2 * cal["lw"], 4)
        side = []
        for c in (ci - dc, ci + dc):
            r = select(runs_in_column(cal, c), cal)
            side.append(None if r is None else (r[0] + r[1]) / 2)
        if None not in side:
            slope = abs(side[1] - side[0]) / (2 * dc) * cal["cpu"] * abs(cal["b"])  # y units per x unit
            dy += slope * cal["xmis"]
        out.append({"x": float(x), "y": float(y), "lo": float(y - dy), "hi": float(y + dy), "px": [float(col), row],
                    "note": f"{what}; {cal['nxt']} x ticks, {cal['nyt']} y ticks, 1 unit x = {cal['cpu']:.0f} px, "
                            f"y misfit {cal['ymis']:.4f}, x misfit {cal['xmis']:.3f}"})
    return out
