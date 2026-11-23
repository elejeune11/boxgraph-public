"""Fig. 2c: gel contraction (% change of diameter) against day, markers of one colour per series.
Axes from the tick marks (x: days 0-3; y: 0-100 by 25). Markers are blobs of the series colour after
an opening that removes the connecting lines; each is assigned to the day tick it sits over (within
40 px). A marker partly hidden under another series' marker is smaller than a whole one: its centre is
then uncertain by the hidden part, which is added to the interval. Markers at the legend's position
(not over a day tick) are ignored. Error bars are not read (see figures.md). See _kit.py."""
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

YTICKS = [0, 25, 50, 75, 100]
XTICKS = [0, 1, 2, 3]


def read_series(image, at, rgb, tol=40):
    ink = K.dark(image, 110.0)
    yl, xl = K.frame(ink)
    # coloured error bars drawn over the y axis cut its dark line short: it runs to the x axis; ticks
    # are longer than the left halves of the black error-bar caps at day 0 (min_len 25)
    # the day-0 marker covers the root of the 0 tick: when 4 ticks are found they are 25-100
    yl = (yl[0], yl[1], yl[2], xl[1])
    yt = sorted(K.side_ticks(ink, yl, "y", -1, min_len=25), reverse=True)
    yax = K.Axis(yt, YTICKS[-len(yt):], what=f"y ticks {yt}")
    xt = sorted(K.side_ticks(ink, xl, "x", +1))
    # in the fibre panel the day-0 tick is drawn over by a coloured error bar: the three ticks found
    # are then days 1-3, and day 0 is extrapolated (the fit's misfit checks the even spacing)
    xax = K.Axis(xt, XTICKS[-len(xt):], what=f"x ticks {xt}")
    m = K.near(image, rgb, tol)
    m[xl[0] + 40:, :] = False
    bl = K.blobs(m, open_px=15, min_area=150)
    full = max((max(b[2], b[3]) for b in bl), default=0.0)
    out = []
    for x in at:
        c = xax.to_px(float(x))
        cand = [b for b in bl if abs(b[0] - c) < 40]
        if not cand:
            out.append({"x": float(x), "y": None, "note": "no marker of this colour over this day: hidden under another series' marker"})
            continue
        b = max(cand, key=lambda t: t[4])
        col, row, h, w, area = b
        hidden = max(full - h, 0.0)
        prec = 2.0 + yax.misfit + hidden
        out.append({"x": float(x), "y": yax.to_val(row), "lo": yax.to_val(row + prec), "hi": yax.to_val(row - prec),
                    "px": [col, row], "px_lo": row + prec, "px_hi": row - prec,
                    "note": f"marker centre at column {col:.0f}, {h:.0f} of {full:.0f} px tall seen; "
                            f"y misfit {yax.misfit:.1f} px, x misfit {xax.misfit:.1f} px"})
    return out
