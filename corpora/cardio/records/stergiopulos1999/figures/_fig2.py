"""Shared reading code for Fig. 2 (PDF p. 4): bar charts of the dog averages with error bars (SE,
as the caption says). Top panel: characteristic impedance (bars Standard, 3-el. WK, 4-el. WK);
bottom panel: total arterial compliance (bars pulse pressure method, area method, 3-el. WK, 4-el. WK).

The figure is a scan, nearly black and white: ink is darker than 128.

Calibration, from the image:
- the y axis is the left one of the two long vertical lines (the frame); the x axis is the long
  horizontal line nearest the bottom;
- the y ticks point outwards, left of the y axis: the short runs of ink 8-24 px left of it, counted
  from the x axis (whose line also reaches left of the axis) upwards, are matched in order to
  0, 0.05, 0.10, ... (labelled ticks 0.0, 0.1, 0.2, ... with an unlabelled tick between each). The
  number of ticks must be `n_ticks`; a straight line is fitted and the largest misfit (px) widens
  every interval.

Bars: on a row 30 px above the x axis, the vertical bar sides are the runs of ink between the two
frame lines; consecutive pairs are the bars, numbered from the left (1, 2, ...). A bar's value is
the centre of its top edge, found going down columns at 25% and 75% of its width (away from the
error bar), the interval half the edge thickness + 2 px + misfit. The error bar is the vertical
stem rising from the top edge near the bar's centre; its upper end is the centre of the cap
(the topmost ink of the stem), read with an interval of half the cap thickness + 2 px + misfit.
The lower half of the error bar is hidden inside the bar and is taken as the mirror of the upper.

`read_bar` returns the bar value with its error bar; `read_se` returns the length of the upper
error bar (cap minus bar top), with an interval combining both ends' precision.
"""

import numpy as np

INK = 128


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def calibrate(image, n_ticks):
    g = image[..., :3].astype(float).mean(axis=2)
    ink = g < INK
    H, W = ink.shape
    cs = ink.sum(axis=0)
    long_cols = np.flatnonzero(cs > 0.9 * cs.max())
    groups = _runs(np.isin(np.arange(W), long_cols))
    (yl, yr), (fl, fr) = groups[0], groups[-1]
    rs = ink[:, yr:fl].sum(axis=1)
    long_rows = np.flatnonzero(rs > 0.9 * (fl - yr))
    rgroups = _runs(np.isin(np.arange(H), long_rows))
    (xt, xb), (tt, tb) = rgroups[-1], rgroups[0]
    band = ink[:, yl - 24: yl - 8].all(axis=1)
    tk = sorted(((a + b - 1) / 2.0 for a, b in _runs(band) if b - a < 25), reverse=True)
    tk = [t for t in tk if t <= xb + 5]
    if len(tk) != n_ticks:
        raise RuntimeError(f"expected {n_ticks} y ticks, found {len(tk)}: {tk}")
    marks = [(t, 0.05 * i) for i, t in enumerate(tk)]
    p = np.array([m[0] for m in marks])
    v = np.array([m[1] for m in marks])
    b, a = np.polyfit(p, v, 1)
    mis = float(np.max(np.abs((v - (a + b * p)) / b)))
    row = xt - 30
    sides = [r for r in _runs(ink[row, yr + 3: fl - 3]) if r[1] - r[0] < 40]
    sides = [(s + yr + 3, e + yr + 3) for s, e in sides]
    if len(sides) % 2:
        raise RuntimeError(f"odd number of bar sides: {sides}")
    bars = [(sides[i][0], sides[i + 1][1]) for i in range(0, len(sides), 2)]
    return dict(ink=ink, a=a, b=b, mis=mis, bars=bars, top=tb, xt=xt, marks=marks)


def _first_run_below(col, start):
    for a, b in _runs(col[start:]):
        return a + start, b + start
    return None


def _bar(cal, k):
    ink = cal["ink"]
    c0, c1 = cal["bars"][k]
    w = c1 - c0
    tops = []
    for f in (0.25, 0.75):
        c = int(c0 + f * w)
        tops.append(_first_run_below(ink[:, c], cal["top"] + 20))
    t0 = float(np.mean([(a + b - 1) / 2.0 for a, b in tops]))
    th = float(np.mean([b - a for a, b in tops]))
    # the stem: the column near the centre with the longest run of ink ending at the top edge
    best = None
    for c in range(int(c0 + 0.35 * w), int(c0 + 0.65 * w)):
        col = ink[:, c]
        r = int(round(t0))
        if not col[r]:
            continue
        top = r
        while top > cal["top"] + 5 and col[top - 1]:
            top -= 1
        if best is None or top < best[1]:
            best = (c, top)
    sc, cap_top = best
    # the cap: the horizontal run at the stem's top; its thickness from the rows the cap spans
    cap_rows = [r for r in range(cap_top, cap_top + 40) if ink[r, sc - 12: sc + 13].all() and ink[r, sc - 14]]
    cap = (min(cap_rows), max(cap_rows) + 1) if cap_rows else (cap_top, cap_top + int(th))
    return dict(c0=c0, c1=c1, top_row=t0, top_th=th, stem=sc, cap=cap)


def read_bar(image, at, n_ticks):
    cal = calibrate(image, n_ticks)
    a, b, mis = cal["a"], cal["b"], cal["mis"]
    out = []
    for x in at:
        k = int(round(float(x))) - 1
        if not 0 <= k < len(cal["bars"]):
            out.append({"x": float(x), "y": None, "note": f"no bar {k + 1}; found {len(cal['bars'])}"})
            continue
        br = _bar(cal, k)
        row = br["top_row"]
        e = br["top_th"] / 2.0 + 2.0 + mis
        crow = (br["cap"][0] + br["cap"][1] - 1) / 2.0
        ce = (br["cap"][1] - br["cap"][0]) / 2.0 + 2.0 + mis
        y = a + b * row
        hi = a + b * crow
        lo = 2 * y - hi
        lrow = 2 * row - crow
        out.append({"x": float(x), "y": y, "lo": a + b * (row + e), "hi": a + b * (row - e),
                    "px": [(br["c0"] + br["c1"]) / 2.0, row], "px_lo": row - e, "px_hi": row + e,
                    "bar_lo": lo, "bar_hi": hi,
                    "bar_lo_outer": a + b * (lrow + ce + e), "bar_hi_outer": a + b * (crow - ce),
                    "note": (f"bar {k + 1}: top edge row {row:.1f} ({br['top_th']:.0f} px thick); SE cap row {crow:.1f}; "
                             "the lower half of the error bar is hidden in the bar and taken as the mirror of the upper")})
    return out


def read_se(image, at, n_ticks):
    cal = calibrate(image, n_ticks)
    a, b, mis = cal["a"], cal["b"], cal["mis"]
    out = []
    for x in at:
        k = int(round(float(x))) - 1
        if not 0 <= k < len(cal["bars"]):
            out.append({"x": float(x), "y": None, "note": f"no bar {k + 1}"})
            continue
        br = _bar(cal, k)
        row = br["top_row"]
        crow = (br["cap"][0] + br["cap"][1] - 1) / 2.0
        # both ends are read in the same image; the calibration offset cancels, its slope does not matter
        e = br["top_th"] / 2.0 + (br["cap"][1] - br["cap"][0]) / 2.0 + 2.0
        se = b * (crow - row)
        lo, hi = sorted((b * (crow - row - e), b * (crow - row + e)))
        out.append({"x": float(x), "y": se, "lo": lo, "hi": hi,
                    "px": [br["stem"], crow], "px_lo": crow - e, "px_hi": crow + e,
                    "note": f"bar {k + 1}: SE = cap (row {crow:.1f}) minus bar top (row {row:.1f}), {row - crow:.1f} px"})
    return out
