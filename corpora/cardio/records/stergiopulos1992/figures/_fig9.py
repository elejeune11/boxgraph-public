"""Fig. 9 (p. 10): systolic pressure / brachial systolic pressure against % femoral stenosis, three
lines. Shared by the three readings of this panel.

Calibration (_figlib.calibrate): x from the inward ticks next to the labels 20-80 and the frame lines
for 0 and 100; y from the inward ticks next to the labels 1.0-0.2 and the frame lines for 1.2 and 0.0;
the small rotation of the scan is measured on the frame lines and taken out.

The legend draws Upper Thigh solid, Knee short-dashed, Ankle long-dash dot. Up to 55 % the three run
flat and apart: dashed (knee) on top, dash-dot (ankle) in the middle, solid (thigh) at the bottom. They
cross near 57-63 %. From 65 % the solid line (thigh) is the top one and rises; below it the dashed
(knee) line lies above the dash-dot (ankle) line; each is traced from 65 % on its own run.
"""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_figlib", Path(__file__).with_name("_figlib.py"))
fl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fl)

XV = [0, 20, 40, 60, 80, 100]
YV = [1.2, 1.0, 0.8, 0.6, 0.4, 0.2, 0.0]
FLAT = {"knee": 0, "ankle": 1, "thigh": 2}
AFTER = {"thigh": 0, "knee": 1, "ankle": 2}  # order of the runs from the top at 65 %


def read(image, at, which):
    d = fl.dark(image)
    fr, X, Y, cal = fl.calibrate(d, XV, YV)
    flat = [x for x in at if x <= 55]
    rest = [x for x in at if x >= 66]
    out = fl.stacked_lines(d, cal, flat, 1.05, 1.185, 3, FLAT[which])
    if rest:
        r_lo, r_hi = int(Y.px(1.19)), int(Y.px(0.3))
        # the first column from 64 % on where all three lines have ink (dashes leave gaps)
        c0 = int(X.px(64.0))
        while len(fl.runs(d[:, c0], r_lo, r_hi)) != 3:
            c0 += 1
            if c0 > X.px(66.0):
                raise ValueError("no column near 65 % shows the three lines apart")
        rs = fl.runs(d[:, c0], r_lo, r_hi)
        a, b = rs[AFTER[which]]
        w = b - a
        mono = "up" if which == "thigh" else "down"
        tr = fl.trace(d, c0, (a + b - 1) / 2.0, int(X.px(96.0)), r_lo, r_hi, max_jump=6, width=w, max_gap=40,
                      monotone=mono)
        out += fl.read_trace(tr, w, rest, cal)
    return out
