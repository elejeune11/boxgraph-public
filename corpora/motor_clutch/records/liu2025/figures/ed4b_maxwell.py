"""Extended Data Fig. 4(b) (PDF p. 68): quasi-steady-state retrograde actin flow predicted for a
Maxwell (liquid-like) substrate at xi_s = 0.1, 1, 10, 100 pN s/nm (the four peach bars under
'Maxwell model', E = 1 MPa).

Shared code in _hd.py. y: the long ticks 0, 40, 80, 120 (the short ones between are 20, 60,
100); x: the category ticks under the bars, used only to find the axis. Bars: columns of the bar
colour reaching the baseline, value at the top edge of the colour; only the columns left of the
first dashed separator (the Maxwell bars) are searched. x is the xi_s printed under each bar.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_hd", Path(__file__).with_name("_hd.py"))
H = importlib.util.module_from_spec(_s)
_s.loader.exec_module(H)

SPEC = {
    "x": {"marks": [(0, 1), (1, 2), (2, 3)], "major": 0.8},
    "y": {"marks": [(0, 0), (1, 40), (2, 80), (3, 120)], "major": 0.8},
}
PEACH = [(247, 200, 150)]
EXP = [(255, 0, 255), (0, 0, 255), (0, 255, 0)]


def read_part(image, frac, colours, labels, top, err=False, **kw):
    cal = H.calibrate(image, SPEC)
    sp = cal["sp"]
    W = image.shape[1]
    box = (max(sp["c1"] + 2, int(frac[0] * W)), int(cal["y"].px(top)), min(sp["x_to"], int(frac[1] * W)), sp["r0"])
    return H.bars(image, colours, 50, cal["y"], box, labels, err=err, **kw)


def read(image, at):
    return read_part(image, (0.0, 0.56), PEACH, [0.1, 1, 10, 100], 125)
