"""Fig. 4a (PDF p. 3): sigma_x and sigma_y against x at a step, from Eqs. 4a and 4b.

Calibration, all from the image (a low-resolution bitmap in the PDF, so lines are about 12 px wide
at 1200 dpi):
- x axis: the long dark row at the bottom of the plot is the x axis and also the stress 0 (the
  label "0" sits at its left end). Below it two ticks hang down: the left one is labelled 0 and
  the right one 20 (um).
- y axis: the long dark column at the left; a tick sticks out to its left at the level labelled
  sigma_0. Stress is read as a fraction of sigma_0: 0 at the x axis row, 1 at that tick.
Only two marks per axis, so no misfit can be computed from them; the interval adds the tick
half-width (each mark's position is uncertain by it) and the line half-width.
Curves: in each column, between the sigma_0 tick and the x axis, the dark runs at least half a
line wide are collected (the dotted step line at x = 0 is avoided by the readings' positions).
The upper run is sigma_y, the lower sigma_x; where the two curves have merged into one run (far
from the step, both near sigma_0) both read that run's centre, and where they touch (one run up to
two lines thick) sigma_y is the run's top plus half a line and sigma_x its bottom minus half a
line. Arrows from the labels touch the curves near x = 3.5-5 um: there a column with more than two
runs takes the two nearest to the medians of neighbouring columns. Each value is the median over
columns within +-4 px.
"""
import numpy as np


def _groups(idx):
    out = []
    for c in idx:
        if out and c - out[-1][-1] <= 1:
            out[-1].append(int(c))
        else:
            out.append([int(c)])
    return out


def calibrate(dk):
    H, W = dk.shape
    # x axis: the longest dark row in the lower part
    frac = dk.mean(1)
    lower = np.arange(H // 2, H)
    ax_rows = [r for r in lower if frac[r] > 0.6 * frac[lower].max()]
    axis_row = float(np.mean(_groups(ax_rows)[0]))
    ar1 = _groups(ax_rows)[0][-1]
    # y axis: the longest dark column in the left part
    fc = dk[: int(axis_row)].mean(0)
    left = np.arange(0, W // 3)
    ay_cols = [c for c in left if fc[c] > 0.6 * fc[left].max()]
    axis_col_g = _groups(ay_cols)[0]
    axis_col = float(np.mean(axis_col_g))
    # x ticks: dark columns hanging below the axis
    band = dk[ar1 + 8:ar1 + 25, axis_col_g[-1] + 20:].mean(0)
    xt = [np.mean(g) + axis_col_g[-1] + 20 for g in _groups(np.where(band > 0.5)[0])]
    assert len(xt) == 2, xt
    xw = max(len(g) for g in _groups(np.where(band > 0.5)[0])) / 2
    # y tick: dark rows sticking out left of the y axis, above the x axis
    band = dk[: int(axis_row) - 20, axis_col_g[0] - 30:axis_col_g[0] - 8].mean(1)
    yt = [np.mean(g) for g in _groups(np.where(band > 0.5)[0])]
    assert len(yt) == 1, yt
    yw = max(len(g) for g in _groups(np.where(band > 0.5)[0])) / 2
    return dict(x0=xt[0], x20=xt[1], xw=xw, r0=axis_row, rs=yt[0], yw=yw, axis_col=axis_col,
                ar1=ar1)


def _runs(dk, c, r_top, r_bot):
    idx = np.where(dk[r_top:r_bot, c])[0] + r_top
    return [(g[0], g[-1]) for g in _groups(idx)]


def _line_width(dk, cal):
    # the commonest run thickness over the right part, where one merged line runs at sigma_0
    r_top = int(cal["rs"] - 80)
    r_bot = int(cal["r0"] - 15)
    c0 = int(cal["x0"] + 0.8 * (cal["x20"] - cal["x0"]))
    th = []
    for c in range(c0, int(cal["x20"]) - 30):
        th += [b - a + 1 for a, b in _runs(dk, c, r_top, r_bot)]
    return float(np.median(th))


def _pair(dk, c, cal, lw):
    r_top = int(cal["rs"] - 80)
    r_bot = int(cal["r0"] - 15)
    runs = [(a, b) for a, b in _runs(dk, c, r_top, r_bot) if b - a + 1 >= 0.5 * lw]
    return runs


def read_curves(image, at, which):
    gray = image.mean(axis=2) if image.ndim == 3 else image
    dk = gray < 128
    cal = calibrate(dk)
    lw = _line_width(dk, cal)
    px_per_um = (cal["x20"] - cal["x0"]) / 20.0
    px_per_s = cal["r0"] - cal["rs"]

    def col_pair(c):
        runs = _pair(dk, c, cal, lw)
        if len(runs) == 1:
            a, b = runs[0]
            if b - a + 1 <= 1.6 * lw:
                return (a + b) / 2, (a + b) / 2, "merged"
            if b - a + 1 <= 2.6 * lw:
                return a + lw / 2, b - lw / 2, "touching"
            return None
        if len(runs) == 2:
            (a1, b1), (a2, b2) = runs
            return (a1 + b1) / 2, (a2 + b2) / 2, "two"
        return None

    out = []
    for x in at:
        x = float(x)
        col = cal["x0"] + x * px_per_um
        ci = int(round(col))
        vals, kinds = [], set()
        for c in range(ci - 4, ci + 5):
            p = col_pair(c)
            if p is not None:
                vals.append(p[:2])
                kinds.add(p[2])
        if len(vals) < 3:
            # more than two runs (an arrow touches): take the runs nearest the neighbours' medians
            ref = []
            for c in list(range(ci - 40, ci - 10)) + list(range(ci + 10, ci + 40)):
                p = col_pair(c)
                if p is not None:
                    ref.append(p[:2])
            if not ref:
                out.append({"x": x, "y": None, "note": "curves not separable here"})
                continue
            ry, rx = np.median([r[0] for r in ref]), np.median([r[1] for r in ref])
            vals = []
            for c in range(ci - 4, ci + 5):
                runs = _pair(dk, c, cal, lw)
                cs = [(a + b) / 2 for a, b in runs]
                if len(cs) >= 2:
                    vals.append((min(cs, key=lambda v: abs(v - ry)), min(cs, key=lambda v: abs(v - rx))))
            kinds.add("arrow")
            if not vals:
                out.append({"x": x, "y": None, "note": "curves not separable here"})
                continue
        row = float(np.median([v[which] for v in vals]))
        y = (cal["r0"] - row) / px_per_s
        # interval: line half-width, the two marks' half-widths, column spread
        spread = float(np.ptp([v[which] for v in vals]))
        dy_px = lw / 2 + cal["yw"] + spread / 2
        dy = dy_px / px_per_s + abs(y) * (cal["yw"] / px_per_s)
        out.append({"x": x, "y": float(y), "lo": float(y - dy), "hi": float(y + dy),
                    "px": [float(col), row],
                    "note": f"line {lw:.0f} px; {'/'.join(sorted(kinds))}; 1 um = {px_per_um:.1f} px, sigma_0 = {px_per_s:.0f} px"})
    return out
