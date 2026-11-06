"""Shared reading code for Fig. 5 (PDF p. 8): area against pressure at the thoracic aorta I midpoint,
elastic (solid line), visco-elastic (dash-dot loop) and visco-elastic with 8 phi (dashed loop).

Calibration, all from the image, with the frame, tick and legend finders of _fig3.py (same MATLAB
style): the inward tick marks on the bottom frame line with a dotted grid line from them, matched
to 11, 12, 13, 14, 15 kPa, and on the left frame line matched to 6.2, 6, 5.8, 5.6 cm^2 (top to
bottom); a straight-line fit whose largest misfit is added to every interval.

The inner band: the elastic line (17 px wide, from the legend sample) runs inside the narrow
visco-elastic loop, which never leaves it by more than about a line width; the 8 phi loop lies
well outside except near its ends. A quadratic in the column is fitted to the centres of the ink
runs in each column (first to the median ink row, then twice to the runs within 30 px of the last
fit). Runs whose centre is within 45 px of that fit form the inner band.
  elas: the elastic line lies somewhere in the inner band: from its top plus half the line's
    vertical thickness (17 px * sqrt(1 + slope^2)) to its bottom less that, widened by 2 px. Where
    the visco-elastic loop is fused with the line this interval holds both; it never singles out
    the visco-elastic loop, which is not read.
  upper8 / lower8: the 8 phi loop's upper and lower branches, the runs whose centre is 45 to 300 px
    above (upper) or below (lower) the fit. One run: its centre, interval its extent less half the
    dashed line's vertical thickness (19 px wide), widened by 2 px. No run (a gap between dashes):
    the straight line between the nearest runs at most 45 columns away on each side, +- 8 px.
    Several separate runs (the small loop the upper branch makes near 13.5 kPa): unreadable.
Every interval also has the calibration misfit and 1 px.
"""

import importlib.util
from pathlib import Path

import numpy as np

W_SOLID, W_DASH = 17.0, 19.0


def _f3():
    spec = importlib.util.spec_from_file_location("alastruey2011_fig3_for5", Path(__file__).with_name("_fig3.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def analyse(image, xlabels, ylabels):
    f3 = _f3()
    g = image[..., :3].astype(float).mean(axis=2)
    dark = g < 128
    fr = f3.frame(dark)
    xt, yt = f3.ticks(dark, fr)
    xa, xb, xm = f3._fit(xt, xlabels, "x axis")
    ya, yb, ym = f3._fit(yt, ylabels, "y axis")
    inside = np.zeros_like(dark)
    inside[fr["top"] + 3:fr["bottom"] - 3, fr["left"] + 3:fr["right"] - 3] = True
    leg = f3._legend(dark, fr)
    if leg is not None:
        inside[max(leg[0], 0):leg[1], max(leg[2], 0):leg[3]] = False
    ink = dark & inside
    cols = np.arange(fr["left"] + 4, fr["right"] - 4)
    runs = {}
    for c in cols:
        rs = [(a, b) for a, b in f3._runs(ink[:, c]) if b - a >= 12]  # grid dots: 8 px at most; lines 17 px or more
        if rs:
            runs[c] = rs
    cs = np.array(sorted(runs), float)
    med = np.array([np.median(np.flatnonzero(ink[:, int(c)])) for c in cs])
    coef = np.polyfit(cs, med, 2)
    for _ in range(2):
        pc, pr = [], []
        for c in cs:
            f = np.polyval(coef, c)
            for a, b in runs[int(c)]:
                m = (a + b - 1) / 2.0
                if abs(m - f) <= 30:
                    pc.append(c)
                    pr.append(m)
        coef = np.polyfit(pc, pr, 2)
    return {"x": (xa, xb, xm), "y": (ya, yb, ym), "runs": runs, "coef": coef, "f3": f3}


def _branch_runs(a, c, which):
    f = np.polyval(a["coef"], c)
    rs = a["runs"].get(c, [])
    out = []
    for r0, r1 in rs:
        m = (r0 + r1 - 1) / 2.0
        d = m - f
        if which == "upper8" and -300 <= d <= -45:
            out.append((r0, r1))
        if which == "lower8" and 45 <= d <= 300:
            out.append((r0, r1))
    return out


def read_spec(image, at, spec):
    a = analyse(image, spec["x"], spec["y"])
    xa, xb, xm = a["x"]
    ya, yb, ym = a["y"]
    which = spec["curve"]
    slope = lambda c: 2 * a["coef"][0] * c + a["coef"][1]  # noqa: E731
    out = []
    for x in at:
        c = int(round((x - xa) / xb))
        h_s = W_SOLID * np.sqrt(1 + slope(c) ** 2)
        h_d = W_DASH * np.sqrt(1 + slope(c) ** 2)
        note = ""
        if which == "elas":
            f = np.polyval(a["coef"], c)
            band = [r for r in a["runs"].get(c, []) if abs((r[0] + r[1] - 1) / 2.0 - f) <= 45]
            if not band:
                out.append({"x": x, "y": None, "note": "no ink near the line"})
                continue
            top, bot = min(r[0] for r in band), max(r[1] for r in band) - 1
            lo, hi = top + h_s / 2 - 2, bot - h_s / 2 + 2
            if hi < lo:
                lo = hi = (top + bot) / 2.0
            note = f"inner band of {len(band)} run(s)"
        else:
            br = _branch_runs(a, c, which)
            if len(br) == 1:
                r0, r1 = br[0]
                lo, hi = r0 + h_d / 2 - 2, r1 - 1 - h_d / 2 + 2
                if hi < lo:
                    lo = hi = (r0 + r1 - 1) / 2.0
                note = "dash"
            elif not br:
                left = next((k for k in range(c - 1, c - 46, -1) if len(_branch_runs(a, k, which)) == 1), None)
                right = next((k for k in range(c + 1, c + 46) if len(_branch_runs(a, k, which)) == 1), None)
                if left is None or right is None:
                    out.append({"x": x, "y": None, "note": "gap with no dash near on both sides"})
                    continue
                yl = np.mean(_branch_runs(a, left, which)[0]) - 0.5
                yr = np.mean(_branch_runs(a, right, which)[0]) - 0.5
                yc = yl + (yr - yl) * (c - left) / (right - left)
                lo, hi = yc - 8.0, yc + 8.0
                note = "gap between dashes"
            else:
                out.append({"x": x, "y": None, "note": "several runs: the branch crosses itself here"})
                continue
        yc = (lo + hi) / 2.0
        pad = ym + 1.0
        lo, hi = lo - pad, hi + pad
        v, v1, v2 = (ya + yb * r for r in (yc, lo, hi))
        out.append({"x": float(x), "y": float(v), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                    "px": [float(c), float(yc)], "px_lo": float(lo), "px_hi": float(hi),
                    "note": f"{note}; x misfit {xm:.1f} px, y misfit {ym:.1f} px"})
    return out
