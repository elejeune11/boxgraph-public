"""Shared reading code for Fig. 1 (PDF p. 4): three bar charts of deviation parameters, four bars each
(left to right, indices 1-4: In vitro 92, In vivo 94, In vivo ESL without and with HD dependence),
means with standard errors over 3 networks (the caption). Black vector art; bars white, grey or black,
each with an upward error bar (stem and cap); the lower half of each error bar is hidden inside its bar.

Calibration, from the image: the frame is found by _kit.frame; the y ticks point outward from the left
frame line (_kit.ticks); the long ticks are matched in order, from the bottom, to the printed labels
the reading passes, and fitted by a straight line; the largest tick misfit is reported and added to
every interval. The x axis is categorical: x is the bar's index.

Bars: in a row 20 px above the bottom frame line, the non-white runs inside the frame are the bars (a
grey or black bar is one wide run; a white bar is a pair of thin outline runs). Its value is the
centre of the top outline stroke: the first dark row from the top, in a column a fifth of the bar's
width from its left edge (clear of the error bar's cap), plus half the stroke width (the vertical run
there for an outlined bar; the white bar's top stroke for a black bar, whose stroke merges with its
fill). The error bar's upper end is the centre of the cap: the first dark run from the top in a column
15 px right of the bar's centre (on the cap, clear of the stem). The lower end is hidden inside the bar
and is taken as the mirror of the upper end about the bar's value.
Intervals (95%): the value +-(1 px + misfit); the error bar's upper end +-(half the cap's thickness +
1 px + misfit), the lower end the same, mirrored.
"""
import importlib.util
from pathlib import Path

import numpy as np

_s = importlib.util.spec_from_file_location("pries2005_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_s)
_s.loader.exec_module(K)


def first_run(v, start):
    i = start
    while i < len(v) and not v[i]:
        i += 1
    j = i
    while j < len(v) and v[j]:
        j += 1
    return i, j


def read_bars(image, at, ylabels):
    g = np.asarray(image, float)[..., :3].mean(axis=2)
    dark = g < 128
    fr = K.frame(dark)
    l0, l1, r0, r1, t0, t1, b0, b1 = fr
    _, yt = K.ticks(dark, fr)
    depth = max(k for _, k in yt)
    ysel = sorted([r for r, k in yt if k > 0.8 * depth], reverse=True)
    if len(ysel) != len(ylabels):
        raise ValueError(f"found {len(ysel)} long y ticks for {len(ylabels)} labels")
    a_, b_, mis = K.fit(ysel, ylabels, False)

    def val(row):
        return float(a_ * row + b_)

    row = b0 - 20
    nonwhite = g[row] < 235
    nonwhite[:l1 + 6] = False
    nonwhite[r0 - 5:] = False
    rr = K.runs(nonwhite)
    bars, thin = [], []
    for a, b in rr:
        if b - a > 100:
            bars.append((a, b))
        else:
            thin.append((a, b))
    for k in range(0, len(thin) - 1, 2):
        bars.append((thin[k][0], thin[k + 1][1]))
    bars.sort()
    # stroke width of an outlined bar's top edge (the first bar whose top stroke is not merged with fill)
    strokes = []
    for a, b in bars:
        c = int(a + 0.2 * (b - a))
        s, e = first_run(dark[:, c], t1 + 3)
        if e - s < 30:
            strokes.append(e - s)
    lw = float(np.median(strokes))
    out = []
    for x in at:
        i = int(round(x)) - 1
        if not 0 <= i < len(bars):
            out.append({"x": x, "y": None, "note": f"only {len(bars)} bars"})
            continue
        a, b = bars[i]
        c = int(a + 0.2 * (b - a))
        s, e = first_run(dark[:, c], t1 + 3)
        ry = s + lw / 2
        cm = int(round((a + b - 1) / 2)) + 15
        cs, ce = first_run(dark[:, cm], t1 + 3)
        if cs >= s - 2:
            out.append({"x": x, "y": None, "note": "no error-bar cap found above the bar"})
            continue
        rc = (cs + ce - 1) / 2
        ec = (ce - cs) / 2 + 1 + mis
        e1 = 1 + mis
        rlo = 2 * ry - rc
        out.append({
            "x": x, "y": val(ry), "lo": val(ry + e1), "hi": val(ry - e1), "px": [(a + b - 1) / 2, ry],
            "px_lo": rlo, "px_hi": rc,
            "bar_hi": val(rc), "bar_lo": val(rlo),
            "bar_hi_outer": val(rc - ec), "bar_lo_outer": val(rlo + ec),
            "note": f"bar columns {a}-{b - 1}, top stroke row {s} (+{lw / 2:.1f}), cap rows {cs}-{ce - 1}; lower "
                    f"end of the error bar hidden in the bar, taken as the mirror of the upper; y ticks "
                    f"{[round(r) for r in ysel]} = {ylabels}, misfit {mis:.2f} px"})
    return out
