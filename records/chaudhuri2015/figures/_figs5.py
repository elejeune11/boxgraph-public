"""Shared reader for Supp. Fig. 5 (cell spreading area against G'' (a) or G'/G'' (b)); the panel
is an embedded bitmap.

- axes: the y-axis and x-axis lines are the long dark runs; ticks are found on the outer side
  of each and matched to the tick values given (labelled and unlabelled ticks, in order).
- markers: dark pixels inside the plot, hole-filled (open squares in b) and opened with a square
  about half a marker wide, so error-bar stems, caps and axes vanish.
- error bars: followed along the dark stem above and below each marker to the centre of its cap.
  Where a stem runs into another marker (the points crowded near x = 0), the end cannot be told
  apart and the bar is not reported.
"""
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)


def read_panel(img, x_ticks, y_ticks, open_px=61, thr=110, cal_px=4.0):
    ink = K.dark(img, thr)
    yl, xl = K.frame(ink)
    yax = K.y_axis_from_ticks(ink, yl, y_ticks, side="left", min_len=15, max_len=160)
    xax = K.x_axis_from_ticks(ink, xl, x_ticks, side="below", min_len=15, max_len=160)
    inner = np.zeros_like(ink)
    inner[: xl[0] - 4, yl[1] + 4:] = ink[: xl[0] - 4, yl[1] + 4:]
    blobs = K.markers(inner, open_px=open_px, min_area=open_px * open_px, split=False)
    s = float(np.median([b[3] for b in blobs]))           # marker size: the median blob width
    split = []
    for b in blobs:
        col, row, h, w, sl = b
        if h <= 1.3 * s:
            split.append(b)
            continue
        # overlapping markers stacked in a column: a square is a pair of horizontal edges
        # (rows almost fully inked across the marker) about one marker size apart
        c0, c1 = int(col - 0.35 * w), int(col + 0.35 * w)
        cov = inner[sl[0], c0:c1].mean(axis=1)
        edges = [(a + sl[0].start, e + sl[0].start) for a, e in K.runs(np.nonzero(cov >= 0.85)[0])]
        used, found = set(), []
        for i, (a, _) in enumerate(edges):
            for j in range(i, len(edges)):
                span = edges[j][1] - a + 1
                if abs(span - s) <= 0.15 * s and i not in used:
                    found.append((col, (a + edges[j][1]) / 2.0, float(span), w, None))
                    used.add(i)
                    break
        split.extend(found)
    blobs = sorted(split, key=lambda t: (t[0], t[1]))
    out = []
    for col, row, h, w, _ in blobs:
        r = K.marker_reading(inner, xax, yax, col, row, h, stem_half=3, cal_px=cal_px)
        # does the stem pass through another marker?
        lo_row, hi_row = r["px_bar"][2], r["px_bar"][1]
        crowd = [b for b in blobs if (b[0], b[1]) != (col, row) and abs(b[0] - col) < max(w, b[3]) and
                 hi_row - b[2] / 2 < b[1] < lo_row + b[2] / 2]
        r["x_lo"] = None
        # the x position: the marker's centre column; its precision is half a bitmap pixel plus misfit
        if crowd:
            for k in ("bar_lo", "bar_hi", "bar_lo_outer", "bar_hi_outer", "px_bar"):
                r.pop(k, None)
            r["note"] += "; error bar not reported: its stem runs into another marker"
        r.pop("x_lo")
        out.append(r)
    return out
