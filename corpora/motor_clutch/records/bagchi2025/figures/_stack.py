"""Stacked two-colour bar charts with two y axes (Fig 9l, S4i Fig): a red segment
(Connected Ligand) with a blue segment (Disconnected Ligand) above it, for a velocity
bar (left axis, blue labels) and a traction bar (right axis, green labels). In both
panels the two axes carry the same labels at the same heights; the green right axis
is calibrated here (its colour is not that of any bar).

  axis    the column with the longest run of green pixels in the right half;
  ticks   green strokes just left of it, matched in order to the printed labels the
          calling file gives (0 at the corner with the x axis, the dark row with the
          longest run in the lower half);
  bars    columns where red or blue stands on the x axis, grouped into bars (first:
          Velocity, second: Traction); in each column the run of bar colour standing on
          the axis is followed upwards (bridging 3 px), and the top of the red and of
          the blue part in that run are taken; the value is the median over the middle
          60% of the bar's columns (a legend patch above a bar is not part of the run).

x is the segment: 1 the top of the red segment, 2 the top of the blue segment.
95% interval: one pixel of edge, the spread of the top over the columns (twice its
s.d.), and the calibration misfit."""
import importlib.util
import os

import numpy as np

_spec = importlib.util.spec_from_file_location("bagchi2025_panel", os.path.join(os.path.dirname(__file__), "_panel.py"))
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)


def read_stack(image, labels, which_bar, tick_len=10):
    green = P.hue_mask(image, 70, 120, smin=40)
    red = P.hue_mask(image, 340, 15, smin=80)
    blue = P.hue_mask(image, 215, 245, smin=60)
    H, W = green.shape
    nd = P._neutral_dark(image)
    r0, r1, _, _ = P._axis_line(nd, "row", 0.5, 1.0)
    runs = [(P._longest_run(green[:, c], gap=2)[0], c) for c in range(W // 2, W)]
    L0, gbest = max(runs)
    good = {c for L, c in runs if L >= 0.8 * L0}
    gc0 = gbest - 1  # the column holding the longest run; tick strokes reach left from it
    strip = green[:, max(0, gc0 - 2 - tick_len):gc0 - 2].sum(axis=1)
    ticks = sorted((t for t in P._ticks(strip, 0, r0, 0.6 * tick_len) if t < r0 - 15), reverse=True)
    if len(ticks) < len(labels):
        raise ValueError(f"green ticks {ticks}, need {len(labels)}")
    marks = list(zip(ticks[:len(labels)], labels)) + [((r0 + r1) / 2.0 + 0.5, 0.0)]
    M = np.array(marks, float)
    b, a = np.polyfit(M[:, 1], M[:, 0], 1)
    mis = max(0.5, float(np.max(np.abs(M[:, 0] - (a + b * M[:, 1])))))
    base = r0 - 8  # above the antialiased edge of the axis line
    anyc = red | blue
    on = [c for c in range(W) if anyc[base - 6:base, c].sum() >= 5]
    bars, cur = [], []
    for c in on + [None]:
        if cur and (c is None or c > cur[-1] + 30):  # an x tick mark interrupts a bar's foot
            if len(cur) >= 10:
                bars.append((cur[0], cur[-1]))
            cur = []
        if c is not None:
            cur.append(c)
    if len(bars) <= which_bar:
        raise ValueError(f"bars found {bars} (x axis row {r0}, {len(on)} columns with colour on it)")
    c0, c1 = bars[which_bar]
    w = c1 - c0 + 1
    tops = {"red": [], "blue": []}
    for c in range(c0 + int(0.2 * w), c1 - int(0.2 * w) + 1):
        r, miss, last = base - 1, 0, base - 1
        while r >= 0 and miss <= 12:
            if anyc[r, c]:
                last, miss = r, 0
            else:
                miss += 1
            r -= 1
        run = range(last, base)
        for name, m in (("red", red), ("blue", blue)):
            rows = [k for k in run if m[k, c]]
            if rows:
                tops[name].append(min(rows))
    out = []
    note = f"right axis: {len(M)} marks misfit {mis:.2f} px; bar columns {c0}-{c1}"
    for x, name in ((1, "red"), (2, "blue")):
        t = tops[name]
        if not t:
            out.append({"x": x, "y": None, "note": f"no {name} segment found"})
            continue
        top, sd = float(np.median(t)), float(np.std(t))
        h = 1.0 + mis + 2 * sd
        y = (top - a) / b
        lo, hi = sorted(((top + h - a) / b, (top - h - a) / b))
        out.append({"x": x, "y": float(y), "lo": float(lo), "hi": float(hi), "px": [(c0 + c1) / 2.0, top],
                    "px_lo": top - h, "px_hi": top + h, "note": f"top of the {name} segment; " + note})
    return out
