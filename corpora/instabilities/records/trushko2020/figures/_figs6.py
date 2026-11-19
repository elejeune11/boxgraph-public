"""Shared reading code for Fig. S6B, C, E, F, G, H, I (PDF p. 28), rendered at 1200 dpi.
These are outputs of the paper's own numerical minimisation of Eq. S2 (B, C, E, G, H, I) and
measurements (F).

Calibration (_cal.py), from tick marks pointing out of the axes:
- linear axes: indexed from the axis crossing or from a labelled tick, with the label step;
- log axes: log_axis() fits the decade length to the major and minor ticks (whole mantissas), from
  one decade tick matched to its label: S6B x 10^-2 at the y axis, y 10^-3 at the x axis (only
  decade ticks are drawn); S6C x 10 at the y axis, y 10^-2 at the x axis; S6G, H, I x 10^-4 at
  the y axis; y: S6G 10^2 at the topmost tick, S6H 10^-2 at the x axis, S6I 10^3 at the topmost
  tick.
Readings:
- S6B (normalised pressure P R^3/K against Delta eps/Delta eps_c, before buckling, Eq. S25): five
  parallel dotted lines, one per normalised compressional rigidity lambda R^2/K = 10^8 (darkest,
  top) to 10^4 (lightest, bottom), as the legend shades and the order of the lines show. They do
  not cross: in a column, the k-th green run from the top is line k (lines that start further
  right are the lower ones, so the k-th run exists wherever line k does).
- S6C (normalised buckling pressure P_B R^3/K against kR^2/lambda): five flat lines, same legend
  and order; they are read in the column kR^2/lambda = 100 (the middle decade) and each reading's
  x is the line's lambda R^2/K from the legend (the panel's own x is not what varies between them).
- S6E (delta/R against Delta eps (%)): magenta, the increasing ramp; green, the decreasing ramp;
  each point a '+' with an SD bar (N = 30). Stems: columns of the series colour with a long
  vertical run; bar ends: the ends of that run; centre: the rows, away from the caps, where the
  colour is wider than the stem (the '+' dash). A point with no visible bar (delta = 0 on the
  increasing ramp) is read at its dash with no bar.
- S6F (delta in um, left axis, blue; Phi in degrees, right axis, orange, against monolayer length
  in um, single folds): the dots; the fitted straight lines are thinner than the opening disk.
- S6G, S6H, S6I (alpha in degrees, delta/R, F_B R^2/K against Delta eps): five curves per panel,
  shades of one hue; each starts at its own buckling threshold and joins the others' common line
  at larger Delta eps (from below in G and H, from above in I). The curve for lambda R^2/K = 10^8
  (lightest) starts first and runs along that common line, so it is the upper envelope of the hue
  in G and H and the lower envelope in I: that envelope is read.
Intervals: half the run (line or dot) height plus 2 px, plus calibration misfit.
"""
import importlib.util
from pathlib import Path

import numpy as np

_s = importlib.util.spec_from_file_location("trushko2020__cal", Path(__file__).with_name("_cal.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

LEGEND = [1e8, 1e7, 1e6, 1e5, 1e4]


def _hue(image, which):
    im = image.astype(int)
    r, g, b = im[:, :, 0], im[:, :, 1], im[:, :, 2]
    if which == "green":
        return (g > r + 25) & (g > b + 5)
    if which == "blue":
        return (b > r + 40) & (b > g + 10)
    return (r > b + 60) & (r > g + 20)          # orange


def _axes(image, panel):
    L = C.axes_lines(image)
    xo, yo = (L["yc0"] + L["yc1"]) / 2, (L["xr0"] + L["xr1"]) / 2
    W = image.shape[1]
    xt = C.ticks_x(L, lim=(L["yc0"] - 3, W))
    yt = C.ticks_y(L)
    if panel == "B":
        return L, C.calibrate_from(xo, xt, 1e-2, 10.0, log=True), C.calibrate_from(yo, yt, 1e-3, 10.0, log=True)
    if panel == "C":
        return L, C.calibrate_from(xo, xt, 10.0, 10.0, log=True), C.calibrate_from(yo, yt, 1e-2, 10.0, log=True)
    if panel == "E":
        return L, C.calibrate_from(xo, xt, 0.0, 0.25), C.calibrate_from(yo, yt, -0.1, 0.1)
    if panel in "GHI":
        xa = C.log_axis(xo, 1e-4, xt, +1)
        if panel == "H":
            ya = C.log_axis(yo, 1e-2, yt, -1)
        else:
            ya = C.log_axis(min(yt), 1e2 if panel == "G" else 1e3, yt, -1)
        return L, xa, ya
    raise ValueError(panel)


def _runs(mask, c, r1):
    idx = np.where(mask[:r1, c])[0]
    return [g for g in C.groups(idx, gap=3) if len(g) >= 3]


def read_lines(image, panel, k=None, at=()):
    L, xa, ya = _axes(image, panel)
    m = _hue(image, "green")
    H, W = m.shape
    m[:, :L["yc1"] + 3] = False
    if panel == "B":
        m[:int(0.3 * H), :int(0.55 * W)] = False     # the legend, upper left
    else:
        m[:int(0.28 * H), :] = False                 # the legend, above the top line
    out = []
    if panel == "C":
        c = int(round(xa.pix(100.0)))
        runs = _runs(m, c, L["xr0"] - 2)
        for lam, g in zip(LEGEND, runs):
            row, half = (g[0] + g[-1]) / 2, (g[-1] - g[0] + 1) / 2
            p = C.point(xa, ya, c, row, 1, half + 2, note=f"line {LEGEND.index(lam) + 1} from the top; read at kR^2/lambda = 100")
            p["x"] = lam
            out.append(p)
        return out
    for x in at:
        c = int(round(xa.pix(float(x))))
        runs = _runs(m, c, L["xr0"] - 2)
        if len(runs) <= k:
            out.append({"x": float(x), "y": None, "note": f"line {k + 1} not present in this column"})
            continue
        g = runs[k]
        row, half = (g[0] + g[-1]) / 2, (g[-1] - g[0] + 1) / 2
        p = C.point(xa, ya, c, row, 1, half + 2, note=f"run {k + 1} from the top")
        p["x"] = float(x)
        out.append(p)
    return out


def read_envelope(image, panel, at):
    L, xa, ya = _axes(image, panel)
    m = _hue(image, {"G": "green", "H": "blue", "I": "orange"}[panel])
    H, W = m.shape
    m[:, :L["yc1"] + 3] = False
    if panel == "I":
        m[int(0.75 * H):, :int(0.45 * W)] = False  # the legend, lower left
    else:
        m[int(0.75 * H):, int(0.55 * W):] = False  # the legend, lower right
    return C.curve_at(m, xa, ya, at, pick="top" if panel in "GH" else "bottom",
                      rowlim=(0, L["xr0"] - 2), note=f"S6{panel} envelope")


def read_ramp(image, which):
    L, xa, ya = _axes(image, "E")
    if which == "increasing":
        m = C.colour(image, (225, 60, 140), 80.0)
    else:
        m = C.colour(image, (60, 160, 70), 80.0)
    H, W = m.shape
    m[:, :L["yc1"] + 3] = False
    m[L["xr0"] - 1:, :] = False
    # arrows (upper part, beside the curves) are short diagonal strokes: kept out by requiring
    # a stem column, a vertical run of at least 12 px
    colsum = np.array([C.longest_run(m[:, c], gap=2)[0] for c in range(W)])
    stems = [g for g in C.groups(np.where(colsum >= 12)[0], gap=2) if len(g) <= 12]
    out = []
    for g in stems:
        c = (g[0] + g[-1]) / 2
        ci = int(round(c))
        n, a, b = C.longest_run(m[:, ci], gap=3)
        top, bot = a, b - 1
        wide = [r for r in range(top + 6, bot - 5) if m[r, ci - 14:ci + 15].sum() >= 10]
        if not wide:
            continue
        gw = max(C.groups(wide, gap=2), key=len)
        row = (gw[0] + gw[-1]) / 2
        bar = (top, bot) if bot - top > 40 else None   # a bare '+' is about 30 px tall
        out.append(C.point(xa, ya, c, row, 2, (gw[-1] - gw[0] + 1) / 2 + 2, bar=bar, bar_px=3.0,
                           note=("" if bar else "no bar visible beside the '+'")))
    return out


def read_4f_like(image, which):
    """S6F: delta (blue, left axis) or Phi (orange, right axis) against monolayer length."""
    L = C.axes_lines(image)
    m0 = L["mask"]
    H, W = m0.shape
    rcol = max(range(int(0.6 * W), W), key=lambda c: C.longest_run(m0[:, c])[0])
    R = C.axes_lines(image, xrow=L["xr0"], ycol=rcol)
    yo = (L["xr0"] + L["xr1"]) / 2
    xt = sorted(t for t in C.ticks_x(L, lim=(L["yc1"] + 5, R["yc0"] - 5)))
    p, idx = C.whole_spacings(xt[0], xt[1:])
    xa = C.Axis(p, [480.0 + 80.0 * k for k in idx])
    if which == "delta":
        ya = C.calibrate_from(yo, C.ticks_y(L), 0.0, 50.0)
        m = _hue(image, "blue")
    else:
        ya = C.calibrate_from(yo, C.ticks_y(R, right=True), 0.0, 30.0)
        m = _hue(image, "orange")
    m[:, :L["yc1"] + 3] = False
    m[:, R["yc0"] - 2:] = False
    m[L["xr0"] - 2:, :] = False
    pts, rad = C.scatter(m, 10, min_area=250)    # dots ~35 px across; the fitted lines are thinner
    out = []
    for c, r, k in sorted(pts):
        e = 3.0 if k == 1 else rad / 2
        out.append(C.point(xa, ya, c, r, e, e, note=(f"split from {k} touching dots" if k > 1 else "")))
    return out
