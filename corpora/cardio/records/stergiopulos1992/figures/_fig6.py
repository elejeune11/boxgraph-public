"""Fig. 6 (p. 8): PI/PIn against % femoral stenosis, two lines. Shared by both readings.

Calibration (_figlib.calibrate): x from the inward ticks next to the labels 20-80 and the frame lines
for 0 and 100; y from the inward ticks next to the labels 1.0-0.2 and the frame lines for 1.2 and 0.0.
The two lines coincide up to about 75 % and separate after it, the dashed one above. Each is traced from
x = 1 % along the only line there: the solid one keeps to the lower edge of the ink when the two
overlap (one line width up from it), the dashed one to the upper edge; where they coincide both get
the same value.
"""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_figlib", Path(__file__).with_name("_figlib.py"))
fl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fl)

XV = [0, 20, 40, 60, 80, 100]
YV = [1.2, 1.0, 0.8, 0.6, 0.4, 0.2, 0.0]


def read_line(image, at, which):
    d = fl.dark(image)
    fr, X, Y, cal = fl.calibrate(d, XV, YV)
    r_lo, r_hi = int(Y.px(1.1)), int(Y.px(0.25))  # the legend lies below 0.25
    c0 = int(X.px(1.5))  # clear of the inward ticks on the left frame
    w = fl.line_width(d, int(X.px(10.0)), r_lo, r_hi)
    prefer = "low" if which == "solid" else "high"
    tr = fl.trace(d, c0, Y.px(1.0), int(X.px(93.0)), r_lo, r_hi, max_jump=8, width=w, prefer=prefer,
                  max_gap=60, monotone="down")
    return fl.read_trace(tr, w, at, cal)
