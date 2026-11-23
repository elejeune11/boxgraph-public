"""Fig. 3(e) (PDF p. 8): measured density of myosin II stacks in NIH-3T3 cells at 1, 10 and
100 ug/ml fibronectin (the light-orange boxes; boxes are mean +- s.e.m., error bars s.d.,
N = 13, 14, 12 cells).

Shared code in _hd.py. y: ticks 0, 2, 4, 6; x: the three category ticks, labelled 1, 10, 100
(log fibronectin axis). Boxes: the light fill colour (the box's mean +- s.e.m.); the value is the
box's middle (the mean) and its interval the box (mean +- s.e.m.). The s.d. whiskers are not
read: the plotted cells' points pile up on their caps. Each box is assigned to the nearest x tick.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_hd", Path(__file__).with_name("_hd.py"))
H = importlib.util.module_from_spec(_s)
_s.loader.exec_module(H)

SPEC = {
    "x": {"scale": "log10", "marks": [(0, 1), (1, 10), (2, 100)], "major": 0.8},
    "y": {"marks": [(0, 0), (1, 2), (2, 4), (3, 6)], "major": 0.8},
}
FILLS = {"nih": ((255, 232, 209), 12), "hela": ((215, 236, 215), 22)}


def read_kind(image, kind, top_value=6.0, **kw):
    cal = H.calibrate(image, SPEC)
    sp = cal["sp"]
    box = (sp["c1"] + 2, int(cal["y"].px(top_value)), sp["x_to"], sp["r0"] - 2)
    rgb, tol = FILLS[kind]
    return H.boxes(image, rgb, tol, cal["x"], cal["y"], box, [1, 10, 100], **kw)


def read(image, at):
    return read_kind(image, "nih", caps=False)
