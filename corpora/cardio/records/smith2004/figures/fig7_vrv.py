# Fig. 7 (p. 8), top-right panel: V_rv against time, one solid curve. Calibration: frame
# left = 0 s with gridlines every 0.5 s; frame bottom = 40 ml with gridlines every 20 ml
# (labels 40 ... 120). The curve is traced from the only run of thick ink at t = 0.15 s,
# so the 'V_rv' and 'SV=70' labels, which do not touch it, are passed by.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_curve", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_curve.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

CFG = {"x_anchor": ("left", 0.0, 0.5), "y_anchor": ("bottom", 40.0, 20.0), "open": 6, "pick": "trace", "seed": [(0.15, "only"), (0.45, "bottom"), (0.75, "top"), (1.2, "only"), (1.45, "only")]}


def read(image, at):
    return C.read_curve(image, at, CFG)
