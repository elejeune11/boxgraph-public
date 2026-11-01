"""Shared reader for Fig. 2b (normalized G' and G'' against frequency, covalent and ionic gels).

- x axis (log10): the decade tick marks hanging from the top frame line, 10^-4 ... 10^0 left to right
  (the same columns as the labelled ticks of the bottom axis, where markers can touch the ticks).
- G' (upper part): the left y axis, ticks at 0.6, 0.8, 1.0 found on its right (inner) side.
- G'' (lower part): the short right y axis, ticks at 0.00, 0.05, 0.10 on its right side.
- markers: pixels of the series colour within the part's rows, hole-filled and opened (lines
  and error-bar stems vanish); touching circles are split where the column height dips.
- error bars: followed along the stem in the series colour above and below the marker; an end
  inside the marker is reported as the marker's edge (at most the marker).
"""
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

COLORS = {"grey": (68, 68, 68), "red": (204, 36, 44)}


def calibrate(img):
    ink = K.dark(img, 40)
    H, W = ink.shape
    vs = K.vlines(ink, int(0.05 * H))
    left = min(vs, key=lambda v: v[0])
    right = max(vs, key=lambda v: v[0])
    if right[0] < W / 2:
        raise ValueError(f"right axis not found: {vs}")
    hs = K.hlines(ink, int(0.5 * W))
    top = min(hs, key=lambda h: h[0])
    xt = K.ticks_x(ink, (top[0], top[1]), (top[2] - 15, top[3] + 15), side="below", min_len=30, max_len=150)
    xt = [p for p, n in xt if n >= 40]
    xax = K.Axis(sorted(xt), [1e-4, 1e-3, 1e-2, 1e-1, 1], log=True, what=f"top ticks {xt}")
    # the 1.0 tick is covered by the first circle marker: the two visible ticks, 0.6 and 0.8
    yl = K.y_axis_from_ticks(ink, left, [0.6, 0.8], side="right", min_len=25, max_len=150)
    # the right axis line is hidden at both ends by the last markers: search its ticks beyond them
    # (the 0.00 tick is crossed by the last open circle, so a tick is a row group with >= 40 px of
    # ink within 100 px right of the axis line, gaps allowed)
    band = ink[:, right[1] + 1:right[1] + 101].sum(axis=1)
    cand = [r for r in range(max(right[2] - 150, 0), min(right[3] + 150, H)) if band[r] >= 40]
    rows = sorted([(a + b) / 2 for a, b in K.runs(cand) if b - a + 1 <= 20], reverse=True)
    yr = K.Axis(rows, [0.0, 0.05, 0.10], what=f"right ticks {rows}")
    right = (right[0], right[1], int(min(rows)), int(max(rows)))
    return xax, yl, yr, left, right


def read_series(img, color, part, tol=45, open_px=25):
    xax, yl, yr, left, right = calibrate(img)
    m = K.near(img, COLORS[color], tol)
    if part == "Gp":
        r0, r1, yax = left[2] - 40, left[3] + 30, yl
    else:
        r0, r1, yax = right[2] - 60, right[3] + 60, yr
    mm = np.zeros_like(m)
    mm[r0:r1, left[1] + 3:] = m[r0:r1, left[1] + 3:]
    out = []
    blobs = K.markers(mm, open_px=open_px, min_area=400)
    hm = float(np.median([b[2] for b in blobs])) if blobs else 0.0
    for col, row, h, w, _ in blobs:
        # a data marker has a neighbour in its series close by in both x and y; the legend's
        # marker stands alone (far below or above its neighbours in x)
        if not any(0 < abs(c2 - col) < 2.8 * hm and abs(r2 - row) < 1.5 * hm for c2, r2, *_ in blobs):
            continue
        r = K.marker_reading(m, xax, yax, col, row, h, stem_half=2)
        r["note"] += f"; marker height {h:.0f} px"
        out.append(r)
    return out
