"""Fig. 4 (p. 7): left posterior tibial pressure against time for 0, 60, 75, 85 and 90 % femoral
stenosis. Shared by the two readings of this panel.

Calibration: x from the inward ticks next to the labels 0.5, 1.0, 1.5 and the frame lines for 0.0 and
2.0 s. The y axis has no tick marks that can be found (none are visible on either side of the frame), so
the centres of the labels 25, 20, ..., 0 stand for them (the corner labels 30 and -5 are moved off
their places and are not used); their spacing is even to a few pixels, which the misfit records. In the
other figures of this paper a label's centre lies within about 0-20 px (at 900 dpi) of its tick, so
the interval is widened by 15 px (about 0.27 kPa) for that unknown offset.

The 90 % line (dash-dot) is the lowest line throughout and the 85 % line (dashed) the second lowest; the
normal, 60 % and 75 % lines lie above both and overlap one another, so they are not read. At each time
the ink within a few columns is pooled and split into lines at gaps; the legend (below about 2.8 kPa,
left of 0.6 s) is kept out.
"""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_figlib", Path(__file__).with_name("_figlib.py"))
fl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fl)

XV = [0.0, 0.5, 1.0, 1.5, 2.0]
YV = [30, 25, 20, 15, 10, 5, 0, -5]


def read(image, at, from_bottom):
    d = fl.dark(image)
    fr, X, Y, cal = fl.calibrate(d, XV, YV, side="labels_y", y_ends="drop", depth=(3, 14))
    out = []
    for t in at:
        y_lo = 2.8 if t < 0.6 else 1.0
        rows = fl.stacked_lines(d, cal, [t], y_lo, 28.0, None, None, win=8, min_gap=10, from_bottom=from_bottom)
        for r in rows:  # widen for the unknown label-to-tick offset (15 px)
            if r.get("y") is not None:
                dv = 15 * abs(Y.b)
                r["lo"], r["hi"] = r["lo"] - dv, r["hi"] + dv
                r["px_lo"], r["px_hi"] = r["px_lo"] - 15, r["px_hi"] + 15
                r["note"] += "; widened 15 px for the label-to-tick offset"
        out += rows
    return out
