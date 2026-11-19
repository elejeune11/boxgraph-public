"""Shared reading code for Fig. S5F, S5G, S5H (PDF p. 27).

S5F: mean capsule thickness (um) against time for one capsule (the contours of S5C), open blue
circles, each the mean of 360 thickness measurements (one per polar angle), error bars SD
(caption). S5G: mean capsule pressure (kPa) against time for the same capsule, open blue circles,
SD error bars. S5H: normalised mean thickness of empty 2.5% capsules (n = 22) against time, the
orange dots (the grey lines behind them are individual capsules and are not read; the SEM bars of
the caption are not visible beside the dots).

Calibration (_cal.py):
- S5F and S5G are boxed plots with ticks pointing into the box, only at the labels. x: the tick
  nearest the y axis (just right of it) is 0, then every 20 h (labels 0, 20, 40). y: the topmost
  tick inside the box is the top label (S5F 35 um, S5G 0.6 kPa), then every label step downwards
  (S5F 5 um: 35, 30, 25, 20, 15; S5G 0.2 kPa: 0.6, 0.4, 0, -0.2; the tick at 0 is hidden by a
  circle). Ticks on the frame lines themselves are left out.
- S5H: ticks point out of the axes, indexed from the crossing; x every 5 h from 0 (labels 0, 10,
  ..., 60 on every second tick); y every 0.05 from 0.75 at the x axis (labels 0,8 to 1,2 with
  decimal commas on every second tick).
Markers: S5F/S5G: the open circles touch their neighbours, so they are found by correlating the
blue pixels with a ring (see rings(): radius chosen from the image, centres at the strongest
peaks at least 1.2 radii apart); S5H: orange pixels opened
with a disk of radius 8 px. Error bars (S5F/S5G): the blue stem through the circle's column,
followed out from the circle's edge to its last blue pixel each way. A bar end that reaches the
plot frame is cut by it (several thickness bars above 35 um, several pressure bars below -0.2
kPa and above 0.7 kPa): that end is taken as the mirror of the other end (SD bars are symmetric),
and the reading says so (an end within 12 px of the frame counts as cut). The circle at t = 0
in S5F and S5G is half hidden behind the y axis frame and is not found. Interval on a marker:
4 px plus calibration misfit.
"""
import importlib.util
from pathlib import Path

import numpy as np

_s = importlib.util.spec_from_file_location("trushko2020__cal", Path(__file__).with_name("_cal.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

TOP = {"F": (35.0, 5.0), "G": (0.6, 0.2)}


def rings(mask):
    """Open circles that touch their neighbours: the mask is correlated with a ring of radius R
    (3 px wide), for R from 18 to 36 px; the R with the strongest peaks is kept, and peaks above
    80% of a full ring, at least 1.2 R apart, are the circles' centres (where two circles overlap,
their arcs make weaker peaks between them, below 80%). Returns (col, row, R)."""
    from scipy.signal import fftconvolve
    m = mask.astype(float)
    best = None
    for R in range(18, 37, 2):
        yy, xx = np.mgrid[-R - 2:R + 3, -R - 2:R + 3]
        d = np.hypot(xx, yy)
        ring = ((d > R - 1.5) & (d < R + 1.5)).astype(float)
        score = fftconvolve(m, ring[::-1, ::-1], mode="same") / ring.sum()
        if best is None or score.max() > best[0].max() + 1e-9:
            best = (score, R)
    score, R = best
    peaks = []
    cand = np.argwhere(score > 0.8)
    order = np.argsort(-score[cand[:, 0], cand[:, 1]])
    for i in order:
        r, c = cand[i]
        if all(np.hypot(r - pr, c - pc) > 1.2 * R for pc, pr, _ in peaks):
            peaks.append((float(c), float(r), float(R)))
    return sorted(peaks)


def read_panel(image, panel):
    L = C.axes_lines(image)
    H, W = image.shape[:2]
    if panel == "H":
        xo, yo = (L["yc0"] + L["yc1"]) / 2, (L["xr0"] + L["xr1"]) / 2
        xa = C.calibrate_from(xo, C.ticks_x(L), 0.0, 5.0)
        ya = C.calibrate_from(yo, C.ticks_y(L), 0.75, 0.05)
        m = C.colour(image, (240, 110, 40), 70.0)
        m[:, :L["yc1"] + 3] = False
        out = []
        for c, r, area in sorted(C.blobs(m, 8, min_area=150)):
            out.append(C.point(xa, ya, c, r, 4, 4))
        return out
    xt = [t for t in C.ticks_x(L, side="in", lim=(L["yc1"] + 4, W)) if t < 0.95 * W]
    xt = sorted(xt)
    p, idx = C.whole_spacings(xt[0], xt[1:])
    xa = C.Axis(p, [20.0 * k for k in idx])
    yt = sorted(t for t in C.ticks_y(L, side="in") if t > 0.05 * H and t < L["xr0"] - 20)
    v_top, step = TOP[panel]
    p, idx = C.whole_spacings(yt[0], yt[1:])
    ya = C.Axis(p, [v_top - step * k for k in idx])
    # the top frame line: the longest ink row in the top tenth
    top_frame = max(range(0, int(0.1 * H)), key=lambda r: C.longest_run(L["mask"][r])[0])
    blue = C.colour(image, (60, 165, 225), 80.0)
    blue[:, :L["yc1"] + 3] = False
    blue[L["xr0"] - 1:, :] = False
    out = []
    for c, r, rad in rings(blue):
        top = C.stem_end(blue, c, r - rad, -1, half=3, gap=4)
        bot = C.stem_end(blue, c, r + rad, +1, half=3, gap=4)
        note = ""
        cut_top, cut_bot = top <= top_frame + 12, bot >= L["xr0"] - 12
        if cut_top and not cut_bot:
            top, note = 2 * r - bot, "upper bar end cut by the frame: taken as the mirror of the lower"
        elif cut_bot and not cut_top:
            bot, note = 2 * r - top, "lower bar end cut by the axis: taken as the mirror of the upper"
        elif cut_top and cut_bot:
            out.append(C.point(xa, ya, c, r, 4, 4, note="both bar ends cut by the frame: bar not read"))
            continue
        out.append(C.point(xa, ya, c, r, 4, 4, bar=(top, bot), bar_px=3.0, note=note))
    return out
