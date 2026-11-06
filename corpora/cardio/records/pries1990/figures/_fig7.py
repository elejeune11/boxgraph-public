"""Reading code for Fig. 7 of Pries et al. 1990: percentage of total pressure head against vessel
diameter, arterial side to the left and venous side to the right of 0. Four series: open
triangles (Zweifach 1974), filled triangles (Zweifach and Lipowsky 1977), open circles (in vitro
viscosity law), filled circles (modified viscosity law).

x: a signed diameter, negative on the arterial side; calibrated on the seven tick marks above the
top frame line, labelled 60, 40, 20, 0, 20, 40, 60 below the panel (read as -60 ... 60).
y: the six ticks left of the frame, labelled 100, 80, 60, 40, 20, 0.

The markers overlap a great deal, so they are found by template matching: each template is the
legend's own glyph for that series (the right-hand glyph of each legend line, found as the ink
blob nearest the given position and centred on it). At each diameter to read, the peaks of the
best-matching template within a narrow column are found; each peak belongs to the template that
matches it best, and the series' value is its strongest peak. A position where that series has no
clear peak, or where two of its peaks compete, is not read.
"""

import os
import sys

import numpy as np
from scipy import ndimage as ndi
from scipy.signal import fftconvolve

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _pts as P  # noqa: E402

X = dict(edge="top", labels=[-60.0, -40.0, -20.0, 0.0, 20.0, 40.0, 60.0], pick=P.longest)
Y = dict(edge="left", labels=[100.0, 80.0, 60.0, 40.0, 20.0, 0.0], pick=P.longest)
# Legend glyphs (column, row in the 800 dpi crop, the right-hand marker of each legend line):
LEGEND_GLYPH = {"open_tri": (1704, 156), "filled_tri": (1704, 227),
                "open_circle": (1709, 364), "filled_circle": (1706, 433)}
LEGEND_BOX = (10.0, 66.0, 70.0, 112.0)  # data units: the legend, not read
R = 26  # template radius, px (a marker is about 36 px across; the template keeps paper round it)
COL_HALF = 20  # px: half width of the column searched at each diameter (5 um is about 75 px)
MIN_SCORE = 0.5  # a peak below this is not a marker
MIN_MARGIN = 0.06  # the series' template must beat every other template there by this much
NMS = 16  # px: peaks closer than this are one peak


def _ncc_maps(img, templates):
    """Masked normalized cross-correlation of the binary image with each template."""
    I = img.astype(float)
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
    mask = (xx * xx + yy * yy <= R * R).astype(float)
    n = mask.sum()
    s1 = fftconvolve(I, mask[::-1, ::-1], mode="same")
    s2 = fftconvolve(I * I, mask[::-1, ::-1], mode="same")
    varI = np.maximum(s2 - s1 * s1 / n, 1e-9)
    out = {}
    for k, T in templates.items():
        t = T.astype(float) * mask
        t0 = (t - t[mask > 0].mean()) * mask
        num = fftconvolve(I, t0[::-1, ::-1], mode="same")
        out[k] = num / np.sqrt(varI * (t0 * t0).sum())
    return out


def _templates(d):
    out = {}
    for k, (c, r) in LEGEND_GLYPH.items():
        win = d[r - R:r + R + 1, c - R:c + R + 1]
        # centre on the ink of the glyph itself (its filled outline)
        sol = ndi.binary_fill_holes(win)
        rr, cc = np.nonzero(sol)
        r2, c2 = int(round(r - R + rr.mean())), int(round(c - R + cc.mean()))
        out[k] = d[r2 - R:r2 + R + 1, c2 - R:c2 + R + 1].copy()
    return out


def read_series(image, at, want):
    d = P.dark(image)
    fr = P.frame(d)
    ax = P.axis(d, fr, **X)
    ay = P.axis(d, fr, **Y)
    maps = _ncc_maps(d, _templates(d))
    keys = sorted(maps)
    stack = np.stack([maps[k] for k in keys])
    best = stack.max(axis=0)
    label = stack.argmax(axis=0)
    r0, r1 = fr["top"][1] + 2, fr["bottom"][0] - 2
    out = []
    cal = f"x misfit {ax['misfit_px']:.1f} px, y misfit {ay['misfit_px']:.1f} px"
    for a in at:
        c = P.to_px(ax, a)
        c0, c1 = int(round(c - COL_HALF)), int(round(c + COL_HALF)) + 1
        sub = best[r0:r1, c0:c1]
        peaks = (sub == ndi.maximum_filter(sub, size=2 * NMS + 1)) & (sub >= MIN_SCORE)
        cand = []
        for pr, pc in zip(*np.nonzero(peaks)):
            row, col = pr + r0, pc + c0
            yv = P.to_val(ay, row)
            if LEGEND_BOX[0] <= a <= LEGEND_BOX[1] and LEGEND_BOX[2] <= yv <= LEGEND_BOX[3]:
                continue
            k = keys[label[row, col]]
            if k == want:
                others = sorted(float(maps[o][row, col]) for o in keys if o != want)
                margin = float(best[row, col]) - others[-1]
                cand.append((float(best[row, col]), row, col, margin))
        cand.sort(reverse=True)
        if not cand:
            out.append({"x": a, "y": None, "note": f"no {want} peak in the column at {a}"})
            continue
        if len(cand) > 1 and cand[1][0] > 0.85 * cand[0][0]:
            out.append({"x": a, "y": None, "note": f"two {want} peaks of similar score in the column at {a}"})
            continue
        s, row, col, margin = cand[0]
        if margin < MIN_MARGIN:
            out.append({"x": a, "y": None, "note": f"the {want} peak at {a} is not clearly that series' glyph (margin {margin:.2f})"})
            continue
        # sub-pixel row: centroid of the score around the peak
        win = maps[want][row - 2:row + 3, col]
        rowf = row + float(np.dot(np.arange(-2, 3), win) / win.sum()) if win.sum() > 0 else float(row)
        err = 3.0 + 2.0 * ay["misfit_px"]
        out.append({"x": a, "y": P.to_val(ay, rowf),
                    "lo": min(P.to_val(ay, rowf + err), P.to_val(ay, rowf - err)),
                    "hi": max(P.to_val(ay, rowf + err), P.to_val(ay, rowf - err)),
                    "px": [float(col), rowf], "px_lo": rowf - err, "px_hi": rowf + err,
                    "note": f"template score {s:.2f}, margin {margin:.2f}; marker x read {P.to_val(ax, col):.1f}; +-{err:.1f} px; {cal}"})
    return out
