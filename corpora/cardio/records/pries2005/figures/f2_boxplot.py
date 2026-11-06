"""Fig. 2 (PDF p. 4): the box plot above the graph, distribution of the measured vessel diameters.

The caption says it marks the 5th, 10th, 25th, 50th, 75th, 90th and 95th percentiles. Read as the
usual box plot: the two circles are the 5th and 95th, the whisker caps the 10th and 90th, the box
edges the 25th and 75th, the line inside the box the 50th percentile. `at` holds the percentiles.

Calibration: the x axis of the graph below (same crop), by the shared code in _kit.py (outward ticks,
long ticks matched to the printed 10 and 100, log scale, minor ticks checked against the decade
pattern). The box plot is everything dark above the graph's top tick marks.
  box: the columns of grey fill (grey 150-230); its outline's vertical edges are the dark column runs
       bounding the fill, the median the dark run inside it;
  whiskers: the long horizontal dark run through the middle of the box plot; the caps are the
       vertical dark runs at its ends;
  circles: the dark components outside the caps; the position is the centre of each ring's bounding box.
Intervals (95%): the position of a line's centre +-(half its width + 1 px + calibration misfit).
"""
import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage

_s = importlib.util.spec_from_file_location("pries2005_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_s)
_s.loader.exec_module(K)


def read(image, at):
    cal = K.calibrate(image, [10, 100], [0, 0.5, 1, 1.5, 2], False, True)
    g = np.asarray(image, float)[..., :3].mean(axis=2)
    top = cal["frame"][4]
    region = slice(0, top - 60)  # above the graph and its outward top ticks
    dark = g[region] < 128
    grey = (g[region] > 150) & (g[region] < 230)
    mis = cal["misfit"]
    gcols = np.flatnonzero(grey.sum(0) > 20)
    g0, g1 = gcols.min(), gcols.max()
    # vertical dark runs in the box rows: columns where many rows are dark
    rows_box = np.flatnonzero(grey[:, (g0 + g1) // 2] | grey[:, g0 + 30])
    r0, r1 = rows_box.min(), rows_box.max()
    vcol = dark[r0:r1 + 1].mean(0) > 0.9
    vruns = K.runs(vcol)
    edges = [(a, b) for a, b in vruns if g0 - 30 <= a and b <= g1 + 30]
    left, right = edges[0], edges[-1]
    inner = [(a, b) for a, b in edges[1:-1]]
    med = max(inner, key=lambda r: r[1] - r[0])
    # whisker: the middle row; its dark extent
    mid = (r0 + r1) // 2
    wr = [(a, b) for a, b in K.runs(dark[mid]) if b - a > 100]
    wa, wb = min(a for a, b in wr), max(b for a, b in wr)
    caps = []
    for c in (wa, wb - 1):
        col = dark[:, max(c - 12, 0):c + 12]
        cc = np.flatnonzero(col[r0:r1].mean(0) > 0.3)
        sub = K.runs(np.isin(np.arange(col.shape[1]), cc))
        a, b = max(sub, key=lambda r: r[1] - r[0])
        caps.append((max(c - 12, 0) + a, max(c - 12, 0) + b))
    # circles: components outside the caps
    lab, n = ndimage.label(dark)
    circ = []
    for sl in ndimage.find_objects(lab):
        ys, xs = sl
        if xs.stop < caps[0][0] - 5 or xs.start > caps[1][1] + 5:
            h, w = ys.stop - ys.start, xs.stop - xs.start
            if 20 < h < 120 and 20 < w < 120:
                circ.append((xs.start, xs.stop, (ys.start + ys.stop) / 2))
    circ.sort()
    if len(circ) != 2:
        raise ValueError(f"found {len(circ)} circles")
    feats = {5: (circ[0][0], circ[0][1], circ[0][2], "left circle", 1.0),
             10: (caps[0][0], caps[0][1], mid, "left whisker cap", None),
             25: (left[0], left[1], mid, "left box edge", None),
             50: (med[0], med[1], mid, "line inside the box", None),
             75: (right[0], right[1], mid, "right box edge", None),
             90: (caps[1][0], caps[1][1], mid, "right whisker cap", None),
             95: (circ[1][0], circ[1][1], circ[1][2], "right circle", 1.0)}
    out = []
    for p in at:
        if int(round(p)) not in feats:
            out.append({"x": p, "y": None, "note": "no such percentile in the box plot"})
            continue
        a, b, row, what, ring = feats[int(round(p))]
        c = (a + b - 1) / 2
        half = 2.0 if ring else (b - a) / 2
        e = half + 1 + mis
        y = 10 ** (cal["ax"] * c + cal["bx"])
        lo = 10 ** (cal["ax"] * (c - e) + cal["bx"])
        hi = 10 ** (cal["ax"] * (c + e) + cal["bx"])
        out.append({"x": p, "y": float(y), "lo": float(lo), "hi": float(hi), "px": [float(c), float(row)],
                    "note": f"{what}, columns {a}-{b - 1}; {cal['note']}"})
    return out
