"""Shared reader for Supp. Fig. 3b (normalized G' and G'' against frequency, all gels; an embedded
bitmap). Only the filled markers (G') of the three ionic gels are read, one colour each.

- x axis (log10): the ticks hanging below the x-axis line, 0.001, 0.01, 0.1, 1 left to right.
- y axis: the ticks left of the y-axis line, 0.0 to 1.0 every 0.2.
- markers: pixels of the series colour in the G' part of the plot (above the 0.4 tick, where
  the G'' markers are not), hole-filled and opened so the connecting line vanishes; the legend
  markers (right of the last data column, below the series) are dropped because they have no
  neighbour of their series close by. A marker partly covered by another series' marker is
  read from what is visible; the interval carries half the marker height when the visible part
  is much smaller than a full marker.
"""
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

COLORS = {"green": (84, 172, 60), "red": (228, 52, 44), "blue": (84, 84, 148)}


def read_series(img, color, tol=60, open_px=25):
    ink = K.dark(img, 60)
    yl, xl = K.frame(ink)
    yax = K.y_axis_from_ticks(ink, yl, [0.0, 0.2, 0.4, 0.6, 0.8, 1.0], side="left", min_len=20, max_len=150)
    xax = K.x_axis_from_ticks(ink, xl, [0.001, 0.01, 0.1, 1], side="below", min_len=20, max_len=150, log=True)
    m = K.near(img, COLORS[color], tol)
    mm = np.zeros_like(m)
    r_hi = int(yax.to_px(0.5))
    mm[: r_hi, yl[1] + 3: xl[3] + 40] = m[: r_hi, yl[1] + 3: xl[3] + 40]
    blobs = K.markers(mm, open_px=open_px, min_area=open_px * open_px)
    hm = float(np.max([b[2] for b in blobs]))
    out = []
    for col, row, h, w, _ in blobs:
        if not any(0 < abs(c2 - col) < 3.5 * hm and abs(r2 - row) < 1.5 * hm for c2, r2, *_ in blobs):
            continue
        part = h < 0.7 * hm
        prec = 4.0 + yax.misfit + (hm / 2 if part else 0.0)
        y = float(yax.to_val(row))
        out.append({"x": float(xax.to_val(col)), "y": y, "lo": float(yax.to_val(row + prec)),
                    "hi": float(yax.to_val(row - prec)), "px": [col, row], "px_lo": row + prec, "px_hi": row - prec,
                    "note": ("partly covered marker; " if part else "") +
                    f"marker centre, height {h:.0f} px; y misfit {yax.misfit:.1f} px, x misfit {xax.misfit:.1f} px"})
    return out
