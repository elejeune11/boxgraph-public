"""Shared reading code for Fig. 6B, 6C and 6D (PDF p. 12), rendered at 1200 dpi.

Fig. 6B: angle (degrees) against delta/R. Read: the red dots (experiments, n = 24 from 3
replicates; the same folds as the blue dots of Fig. 4H), the dark grey dots (simulation means,
"simul mean 2%", n = 39 points averaged from the 1,297), the green line (alpha) and the purple
line (gamma) of continuum theory. The light grey cloud (1,297 individual simulation points)
overlaps itself and is not read. The alpha line cuts one red dot (near delta/R = 0.33) in two:
two red fragments each under 70% of a dot's area whose centres are less than a dot diameter
apart are joined by a dot-sized disk at their common centre.
Calibration (_cal.py): x ticks below the axis every 0.1 from 0 at the y axis (labels 0, 0.2, ...,
1.0 on every second tick); y ticks left of the axis every 5 degrees from 0 at the x axis (labels
0, 10, ..., 70 on every second tick).

Fig. 6C: mean pressure (Pa) against normalised cell number. Read: the red dots (experiments,
n = 53 from 5 replicates) with their red SD error bars, and the dark grey dots (simulations,
n = 184), read as a curve at given x (the dots overlap into a band; their grey SD bars are
lighter and thinner and are not read). Calibration: x ticks below the axis every 0.25 from 1.0
at the y axis (labels 1.0, 1.5, 2.0 on every second tick); y ticks left of the axis every 50 Pa,
indexed from the top tick, labelled 500 (labels 500 down to -100 on every second tick; the x
axis sits below the lowest tick, so it is not a mark).

Fig. 6D: pressure (Pa) against cell number, mean pressure of 41 simulations for three pairs of
normalised parameters (magenta k^s 0.01 c^b 0.02, blue k^s 0.01 c^b 0.1, green k^s 0.18 c^b 0.1),
the dots. Their SD bars are drawn in darker shades of the same hues over 41 thin traces each of
those hues, and cannot be told from them reliably: they are not read. The dots of a series touch
each other (one per cell number) and hide each other where the series cross, so only dots found
singly are kept; runs of touching dots (magenta and green above 70 cells, most of the blue
series) are left out rather than split; a kept dot may be partly hidden by another series, so
its interval is half a dot radius. Calibration: x ticks below
the axis every 5 cells from 40 at the y axis (labels 40, 50, ..., 80 on every second tick); y
ticks left of the axis every 50 Pa from 0 at the x axis (labels 0, 100, ..., 500 on every
second tick).

Dots: pixels near the series colour (sampled from the image) opened with a disk (radius 7 px; a
dot is 25-35 px across, lines and traces are thinner), touching dots split by area. Interval:
4 px on a dot's centre (half a radius for a dot split from touching ones) plus misfit.
"""
import importlib.util
from pathlib import Path

import numpy as np

_s = importlib.util.spec_from_file_location("trushko2020__cal", Path(__file__).with_name("_cal.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)


def _cal(image, panel):
    L = C.axes_lines(image)
    xo, yo = (L["yc0"] + L["yc1"]) / 2, (L["xr0"] + L["xr1"]) / 2
    W = image.shape[1]
    if panel == "6B":
        xa = C.calibrate_from(xo, C.ticks_x(L), 0.0, 0.1)
        ya = C.calibrate_from(yo, C.ticks_y(L), 0.0, 5.0)
    elif panel == "6C":
        xa = C.calibrate_from(xo, C.ticks_x(L), 1.0, 0.25)
        yt = sorted(C.ticks_y(L))
        p, idx = C.whole_spacings(yt[0], yt[1:])
        ya = C.Axis(p, [500.0 - 50.0 * k for k in idx])
    else:
        xa = C.calibrate_from(xo, C.ticks_x(L, lim=(L["yc1"], W)), 40.0, 5.0)
        ya = C.calibrate_from(yo, C.ticks_y(L), 0.0, 50.0)
    return L, xa, ya


def _dots(image, L, xa, ya, mask, radius=7, legend=None, bars=None, singles_only=False):
    mask = mask.copy()
    mask[L["xr0"] - 2:, :] = False
    mask[:, :L["yc1"] + 2] = False
    if legend:
        a0, b0, a1, b1 = legend
        mask[b0:b1, a0:a1] = False
    pts, rad = C.scatter(mask, radius, min_area=150)
    out = []
    for c, r, k in sorted(pts):
        if singles_only and k > 1:
            continue
        e = 4.0 if (k == 1 and not singles_only) else rad / 2   # 6D: dots partly hidden by others
        bar = None
        if bars is not None:
            top = C.stem_end(bars, c, r - rad, -1, half=2, gap=6)
            bot = C.stem_end(bars, c, r + rad, +1, half=2, gap=6)
            bar = (top, bot)
        out.append(C.point(xa, ya, c, r, e, e, bar=bar, bar_px=3.0,
                           note=(f"split from {k} touching dots" if k > 1 else "")))
    return out


def _neutral(image, lo, hi):
    im = image.astype(float)
    v = im.mean(axis=2)
    return (v > lo) & (v < hi) & (im.max(axis=2) - im.min(axis=2) < 25)


def read(image, at, panel, what):
    L, xa, ya = _cal(image, panel)
    H, W = image.shape[:2]
    if panel == "6B":
        legend = (int(0.55 * W), int(0.68 * H), W, H)       # the legend, lower right (no data there)
        if what == "exp":
            # the alpha line crosses one red dot and cuts it in two: two fragments each under
            # 70% of a dot's area whose centres are less than a dot diameter apart are one dot
            red = C.colour(image, (225, 30, 30), 70.0)
            red[L["xr0"] - 2:, :] = False
            red[:, :L["yc1"] + 2] = False
            a0, b0, a1, b1 = legend
            red[b0:b1, a0:a1] = False
            opened = C.ndimage.binary_opening(red, structure=np.ones((9, 9), bool))
            lab, n = C.ndimage.label(opened)
            bl = [np.where(lab == i) for i in range(1, n + 1)]
            bl = [(float(cc.mean()), float(rr.mean()), len(rr)) for rr, cc in bl if len(rr) >= 150]
            med = float(np.median([b[2] for b in bl]))
            diam = 2 * np.sqrt(med / np.pi)
            small = [b for b in bl if b[2] < 0.7 * med]
            merged, used = [], set()
            for i, a in enumerate(small):
                for j, b in enumerate(small):
                    if j > i and i not in used and j not in used and np.hypot(a[0] - b[0], a[1] - b[1]) < diam:
                        w = a[2] + b[2]
                        merged.append(((a[0] * a[2] + b[0] * b[2]) / w, (a[1] * a[2] + b[1] * b[2]) / w, w))
                        used |= {i, j}
            m2 = opened.copy()
            yy, xx = np.ogrid[:m2.shape[0], :m2.shape[1]]
            for c, r, area in merged:   # fill the cut: a dot-sized disk at the pair's centre
                m2 |= (xx - c) ** 2 + (yy - r) ** 2 <= (diam / 2) ** 2
            return _dots(image, L, xa, ya, m2, radius=7, legend=legend)
        if what == "simmean":
            return _dots(image, L, xa, ya, _neutral(image, 40, 100), radius=9, legend=legend)
        rgb = (20, 120, 50) if what == "alpha" else (60, 50, 140)
        m = C.colour(image, rgb, 70.0)
        m[int(0.68 * H):, int(0.55 * W):] = False
        m[:, :L["yc1"] + 3] = False
        return C.curve_at(m, xa, ya, at, pick="top" if what == "alpha" else "bottom",
                          rowlim=(0, L["xr0"] - 2), note=what)
    if panel == "6C":
        legend = (L["yc1"] + 5, 0, int(0.6 * W), int(0.2 * H))
        if what == "exp":
            red = C.colour(image, (210, 10, 10), 80.0)
            red[:int(0.2 * H), :int(0.6 * W)] = False
            # dots are about 40 px across; where several bars stand side by side (x > 2.1) they
            # are thicker than a single bar, so the disk is larger here
            return _dots(image, L, xa, ya, red, radius=13, legend=legend, bars=red)
        m = _neutral(image, 50, 110)
        m[:int(0.2 * H), :int(0.6 * W)] = False
        m[:, :L["yc1"] + 3] = False
        # the dots overlap into a band; open away the thin bars and caps first
        m = C.ndimage.binary_opening(m, structure=np.ones((9, 9), bool))
        return C.curve_at(m, xa, ya, at, pick="largest", rowlim=(0, L["xr0"] - 2),
                          note="simulations; the band of overlapping dots")
    rgb = {"magenta": (166, 15, 91), "blue": (5, 108, 172), "green": (18, 96, 48)}[what]
    legend = (L["yc1"] + 5, 0, int(0.55 * W), int(0.3 * H))
    return _dots(image, L, xa, ya, C.colour(image, rgb, 45.0), radius=9, legend=legend, singles_only=True)
