"""Extended Data Fig. 4(a) (PDF p. 68): quasi-steady-state cell traction predicted for a Maxwell
(liquid-like) substrate at xi_s = 0.1, 1, 10, 100 pN s/nm (the four peach bars under 'Maxwell
model', E = 1 MPa).

Shared code in _hd.py (via ed4b_maxwell). y: the long ticks 0, 60, 120, 180 (the short ones
between are 30, 90, 150); x: category ticks, used only to find the axis. Only the columns left of
the dashed separator are searched; x is the xi_s printed under each bar.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_ed4bm", Path(__file__).with_name("ed4b_maxwell.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)
SPEC = {"x": B.SPEC["x"], "y": {"marks": [(0, 0), (1, 60), (2, 120), (3, 180)], "major": 0.8}}


def read(image, at):
    cal = B.H.calibrate(image, SPEC)
    sp = cal["sp"]
    box = (sp["c1"] + 2, int(cal["y"].px(185)), int(0.8 * image.shape[1]), sp["r0"])
    return B.H.bars(image, B.PEACH, 50, cal["y"], box, [0.1, 1, 10, 100])
