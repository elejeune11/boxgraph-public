"""Black bar charts of Fig. 2(d) (PDF p. 4): raster MATLAB panels with a grey frame and solid black bars.

Calibration: the frame is the kit's (`_kit.frame`: the grey box's full rows and columns). Ticks are small
dark blobs (area < 500) just inside the frame: x ticks in a 45 px band below the top side only (the bars
hide the bottom ones), blobs closer than 30 px merged, matched to the inner printed labels 2, 4, 6; y ticks
on one side only, the side whose ticks the bars leave clear (a 45 px band inside the left or the right
side), matched to the inner labels 0.8, 0.6, 0.4, 0.2 (0 and 1 sit on the frame's corners). The fit and
misfit are the kit's (_fit). The edge of a bar is searched only from 30 rows above its dark top, so a
tick beside a bar standing against the frame is not taken for it.

Bars: connected regions of dark pixels (grey < 90) larger than 20000 px that reach the bottom of the
frame. The bar nearest each requested x (its centre column) is taken if it lies within a quarter of
a 0.5 um bin. The raster is blurred, so the top edge is found on the mean grey profile of the bar's
middle half of columns: the first row from the top where the profile falls below half-way between the
paper (median grey above the bar) and the bar's own black (median grey of its middle). Interval: +/-
(the blur width, i.e. the number of rows the profile takes to go from 25% to 75% of that step, at
least 2 px, searched within 30 rows of the edge, plus the y misfit, plus 4 px for where the centre of a
thick blurred tick lies: the full-height bars of the paxillin panel, which must be at 1 (the maximum),
read 0.995, about 4 px low), converted to values. A bar that reaches the top frame is noted.
"""
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("craig2015_kit_bb", Path(__file__).with_name("_kit.py"))
_kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kit)

XLABELS = [2, 4, 6]
YLABELS = [0.8, 0.6, 0.4, 0.2]


def _merge(vals, gap=30):
    out = []
    for v in sorted(vals):
        if out and v - out[-1][-1] < gap:
            out[-1].append(v)
        else:
            out.append([v])
    return [float(np.mean(m)) for m in out]


def calibrate(image, xlabels, yside="left"):
    L, T, R, B = _kit.frame(image)
    g = _kit._gray(image)
    small = [b for b in _kit._blobs(g < 90) if b["area"] < 500]
    xs = _merge([b["c"] for b in small if T - 3 <= b["r"] <= T + 45 and L + 12 < b["c"] < R - 12])
    if yside == "left":
        ys = _merge([b["r"] for b in small if L - 3 <= b["c"] <= L + 45 and T + 12 < b["r"] < B - 12])
    else:
        ys = _merge([b["r"] for b in small if R - 45 <= b["c"] <= R + 3 and T + 12 < b["r"] < B - 12])
    kx, cx, mx = _kit._fit(np.array(xs), xlabels)
    ky, cy, my = _kit._fit(np.array(ys), YLABELS)
    return {"frame": (L, T, R, B), "kx": kx, "cx": cx, "mx": mx, "ky": ky, "cy": cy, "my": my}


def read(image, at, xlabels=XLABELS, yside="left"):
    cal = calibrate(image, xlabels, yside)
    L, T, R, B = cal["frame"]
    g = _kit._gray(image)
    bars = [b for b in _kit._blobs(g < 90) if b["area"] > 20000 and b["r1"] >= B - 15 and L - 5 < b["c"] < R + 5]
    ky = abs(cal["ky"])
    px_per_x = abs(1.0 / cal["kx"])
    out = []
    for x in at:
        c = (x - cal["cx"]) / cal["kx"]
        near = [b for b in bars if abs(b["c"] - c) < 0.25 * 0.5 * px_per_x]
        if not near:
            out.append({"x": x, "y": None, "note": "no bar found at this x"})
            continue
        b = min(near, key=lambda b: abs(b["c"] - c))
        w = b["c1"] - b["c0"]
        c0, c1 = int(b["c0"] + w / 4), int(b["c1"] - w / 4)
        prof = g[:, c0:c1].mean(axis=1)
        top_dark = b["r0"]
        black = float(np.median(prof[top_dark + 10:B - 10]))
        paper_rows = prof[max(T + 3, top_dark - 60):max(T + 4, top_dark - 15)]
        paper = float(np.median(paper_rows)) if len(paper_rows) else 255.0
        half = 0.5 * (paper + black)
        rows = np.arange(len(prof))
        cand = rows[(rows >= max(T - 2, top_dark - 30)) & (rows <= top_dark + 20) & (prof < half)]
        edge = int(cand.min()) if len(cand) else top_dark
        q1, q3 = paper - 0.25 * (paper - black), paper - 0.75 * (paper - black)
        win = (rows >= max(T + 3, edge - 30)) & (rows <= edge + 30)
        r25 = rows[win & (prof < q1)]
        r75 = rows[win & (prof < q3)]
        blur = max(2.0, float(r75.min() - r25.min())) if len(r25) and len(r75) else 4.0
        y = cal["ky"] * edge + cal["cy"]
        e = (blur + cal["my"] + 4) * ky
        note = f"top edge of the bar at column {b['c']:.0f} (expected {c:.0f}); blur {blur:.0f} px"
        if edge <= T + 3:
            note += "; the bar reaches the top of the frame (value 1, the maximum)"
        out.append({"x": x, "y": y, "lo": y - e, "hi": y + e, "px": [b["c"], edge], "note": note})
    return out
