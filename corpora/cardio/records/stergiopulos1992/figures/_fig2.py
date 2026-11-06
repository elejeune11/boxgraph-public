"""Fig. 2 (p. 6): predicted waveforms for the control case, (a) pressure and (b) flow, over two
cycles. Shared by the readings of both panels.

Calibration (_figlib.calibrate): x from the inward ticks next to the labels 0.5, 1.0, 1.5 and the frame
lines for 0.0 and 2.0 s; y from the inward ticks next to the inner labels and the frame lines for the
end labels; the small rotation of the scan is measured on the frame lines and taken out.

Only what can be told apart is read: in (b) the proximal boundary condition (the large solid pulse,
the topmost ink while it rises and peaks), in (a) the highest peak of each cycle (the femoral artery,
dash-dot: its peaks stand clear above all other lines).
"""

import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("_figlib", Path(__file__).with_name("_figlib.py"))
fl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fl)

XV = [0.0, 0.5, 1.0, 1.5, 2.0]
PANEL = {"a": [30, 20, 10, 0], "b": [600, 400, 200, 0, -200]}


def _cal(image, panel):
    d = fl.dark(image)
    if panel == "a":  # the y ticks of (a) are bumps of a few pixels: the label centres stand for them
        fr, X, Y, cal = fl.calibrate(d, XV, PANEL[panel], side="labels_y", depth=(3, 14))
    else:
        fr, X, Y, cal = fl.calibrate(d, XV, PANEL[panel], depth=(3, 14))
    return d, fr, X, Y, cal


def topmost(image, at, panel, y_lo, y_hi):
    """At each time, the topmost run of ink between y_lo and y_hi, read at its centre (on a steep edge
    the run is long and its centre is the line's value at that column); the interval is the run."""
    d, fr, X, Y, cal = _cal(image, panel)
    out = []
    for t in at:
        c = cal.col(t, Y.px(0.5 * (y_lo + y_hi)))
        rs = fl.runs(d[:, int(round(c))], int(Y.px(y_hi)), int(Y.px(y_lo)))
        if not rs:
            out.append({"x": t, "y": None, "note": "no ink here"})
            continue
        a, b = rs[0]
        r = (a + b - 1) / 2.0
        half = (b - a) / 2.0 + Y.misfit_px
        out.append(fl.reading(t, r, c, half, cal, f"topmost run, rows {a}-{b - 1}; {cal.note()}"))
    return out


def peaks(image, panel, windows, y_lo, y_hi):
    """The highest ink in each time window: its time (the middle of the columns that reach the top row
    of ink, within one line width) and value (one half line width below the top edge)."""
    d, fr, X, Y, cal = _cal(image, panel)
    out = []
    r_top, r_bot = int(Y.px(y_hi)), int(Y.px(y_lo))
    for t0, t1 in windows:
        c0, c1 = int(X.px(t0)), int(X.px(t1))
        tops = []
        for c in range(c0, c1):
            rs = fl.runs(d[:, c], r_top, r_bot)
            if rs:
                tops.append((rs[0][0], c, rs[0][1] - rs[0][0]))
        top = min(t[0] for t in tops)
        near = [t for t in tops if t[0] <= top + 1]
        c = float(np.mean([t[1] for t in near]))
        w = float(np.median([t[2] for t in tops if t[2] < 20]))  # thickness of the line where it is not steep
        r = top + (w - 1) / 2.0
        half = w / 2.0 + Y.misfit_px
        t = X.val(cal.cs(c, r))
        out.append(fl.reading(round(t, 4), r, c, half, cal, f"peak in {t0}-{t1} s, line {w:.0f} px; {cal.note()}"))
    return out
