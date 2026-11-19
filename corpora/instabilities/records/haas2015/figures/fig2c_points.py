"""Fig. 2(c) (PDF p. 3): the numerical results for Phi (green + markers) against f.

Calibration, all from the image:
- axes: the longest dark column in the left third is the Phi axis, the longest dark row in the
  lower third is the f axis.
- ticks: short dark runs crossing each axis. Labels are dark blobs left of the Phi axis and below
  the f axis; the two labelled values are 1.0 and 0.8 on both axes (the upper / right label is
  1.0). Each label is matched to the tick nearest its centre, and the unlabelled ticks are
  checked to fall on the same linear scale (the misfit enters the interval).
Markers: green pixels (G well above R). Along the line, the green height per column is the
line's slanted thickness; the vertical arm of a + makes it much taller. Columns taller than
1.6 times the median are grouped; each group is one marker, at the group's centre column and
the mid-row of its green extent. Interval: a quarter of the arm length (where along its arm the
centre is) plus the calibration misfit.
"""
import numpy as np


def _groups(idx, gap=1):
    out = []
    for c in idx:
        if out and c - out[-1][-1] <= gap:
            out[-1].append(int(c))
        else:
            out.append([int(c)])
    return out


def _axes(dk):
    H, W = dk.shape
    colsum = dk.sum(0)
    c_axis = int(np.argmax(colsum[: W // 3]))
    rowsum = dk.sum(1)
    r_axis = int(H * 2 // 3 + np.argmax(rowsum[H * 2 // 3:]))
    return c_axis, r_axis


def _ticks_y(dk, c_axis, r_axis, lw):
    # short dark runs crossing the axis column (ticks stick out on both sides)
    left = dk[:, max(c_axis - 2 * lw, 0): c_axis - lw].mean(1)
    right = dk[:, c_axis + lw: c_axis + 2 * lw].mean(1)
    rows = np.where((left > 0.6) & (right > 0.6))[0]
    rows = rows[rows < r_axis - 4 * lw]
    return [float(np.mean(g)) for g in _groups(rows) if len(g) <= 3 * lw]


def _ticks_x(dk, c_axis, r_axis, lw):
    below = dk[r_axis + lw: r_axis + 2 * lw, :].mean(0)
    above = dk[max(r_axis - 2 * lw, 0): r_axis - lw, :].mean(0)
    cols = np.where((below > 0.6) & (above > 0.6))[0]
    cols = cols[cols > c_axis + 4 * lw]
    return [float(np.mean(g)) for g in _groups(cols) if len(g) <= 3 * lw]


def _blobs(mask):
    from scipy import ndimage
    lab, n = ndimage.label(mask)
    return [ndimage.find_objects(lab)[i] for i in range(n)], lab


def _fit(ticks, labelled):
    """labelled: [(pixel of label centre, value)] -> fit value = a + b*pixel through the ticks."""
    t = np.array(sorted(ticks))
    pairs = []
    for p, v in labelled:
        pairs.append((t[np.argmin(np.abs(t - p))], v))
    (p1, v1), (p2, v2) = pairs
    b = (v2 - v1) / (p2 - p1)
    a = v1 - b * p1
    # unlabelled ticks between and beyond: on a regular grid of the tick spacing
    step = np.median(np.diff(t))
    resid = []
    for tt in t:
        v = a + b * tt
        k = (v - v1) / (b * step)
        resid.append(abs(k - round(k)) * abs(b) * step)
    return a, b, float(max(resid))


def read(image, at):
    img = image.astype(float)
    gray = img.mean(axis=2)
    R, G, B = img[..., 0], img[..., 1], img[..., 2]
    green = (G - R > 50) & (G - B > 10)
    dk = (gray < 170) & ~green
    H, W = dk.shape
    c_axis, r_axis = _axes(dk)
    # line width of the axes: thickness of the f axis at three quarters of the width
    c_mid = int(c_axis + 0.75 * (W - c_axis))
    run = [g for g in _groups(np.where(dk[:, c_mid])[0]) if g[0] <= r_axis <= g[-1]]
    lw = max(2, len(run[0]) if run else 2)
    yt = _ticks_y(dk, c_axis, r_axis, lw)
    xt = _ticks_x(dk, c_axis, r_axis, lw)
    # keep the ticks on one regular grid (drops the arrowheads and the axis break), as in _fig3.py
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("haas2015_fig3", Path(__file__).with_name("_fig3.py"))
    f3 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(f3)
    yt, ysp = f3.regular(yt)
    xt, xsp = f3.regular(xt)
    # the arrowhead at the end of the f axis is not a tick
    # (the ends of the axis lines: the dark runs through the axes' middles)
    c_ref = int(c_axis + 0.75 * (W - c_axis))
    tip = [g for g in _groups(np.where(dk[r_axis, :])[0]) if g[0] <= c_ref <= g[-1]][0][-1]
    xt = [t for t in xt if t < tip - 0.35 * xsp]
    r_ref = int(np.median(yt))
    ytip = [g for g in _groups(np.where(dk[:, c_axis])[0]) if g[0] <= r_ref <= g[-1]][0][0]
    yt = [t for t in yt if t > ytip + 0.35 * ysp]
    # labelled ticks: a tick with printed digits beside it (left of the Phi axis, below the f axis)
    ycent = []
    for t in sorted(yt):
        win = dk[int(t - ysp / 6): int(t + ysp / 6), 0: c_axis - 4 * lw]
        if win.size and win.sum() > 6 * lw * lw:
            ycent.append(t)
    xcent = []
    for t in sorted(xt):
        c0 = max(int(t - xsp / 2), 0)
        win = dk[r_axis + 4 * lw: r_axis + int(0.9 * xsp), c0: int(t + xsp / 2)]
        if win.size and win.sum() > 6 * lw * lw:
            cent = c0 + float(np.mean(np.where(win)[1]))
            if abs(cent - t) < xsp / 8:   # digits centred under the tick (not the italic axis name f)
                xcent.append(t)
    assert len(ycent) == 2, ycent
    assert len(xcent) == 2, xcent
    ay, by, my = _fit(yt, [(ycent[0], 1.0), (ycent[1], 0.8)])   # upper label 1.0
    ax, bx, mx = _fit(xt, [(xcent[0], 0.8), (xcent[1], 1.0)])   # left label 0.8
    # markers
    gh = []
    tops, bots = {}, {}
    for c in range(c_axis + 1, W):
        rr = np.where(green[:, c])[0]
        if len(rr):
            tops[c], bots[c] = rr.min(), rr.max()
            gh.append(rr.max() - rr.min() + 1)
    med = float(np.median(gh))
    tall = [c for c in tops if bots[c] - tops[c] + 1 > 1.6 * med]
    out = []
    for g in _groups(tall):
        if len(g) < 2:
            continue
        cc = float(np.mean(g))
        rows = [(tops[c] + bots[c]) / 2 for c in g]
        rr = float(np.median(rows))
        arm = float(np.median([bots[c] - tops[c] + 1 for c in g]))
        x = ax + bx * cc
        y = ay + by * rr
        dy = abs(by) * arm / 4 + my
        out.append({"x": float(x), "y": float(y), "lo": float(y - dy), "hi": float(y + dy),
                    "px": [cc, rr],
                    "note": f"+ marker, arm {arm:.0f} px; 0.1 in Phi = {abs(0.1 / by):.0f} px; misfit x {mx:.4f}, y {my:.4f}"})
    return out
