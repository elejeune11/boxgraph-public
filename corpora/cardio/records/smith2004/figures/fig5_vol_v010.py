# Fig. 5 (p. 7), top panel: chamber volume of the single-chamber model, the solid curve
# (V0 = 10 ml, labelled). Calibration: solid left axis = 0 s, gridlines every 0.2 s (labels
# 0 ... 1.8, the dotted right edge is 1.8); solid bottom axis = 0 ml, gridlines every 20 ml
# (labels 0 ... 100). Traced from the lower of the two curves at t = 0.1 s and the only
# curve at t = 0.7, 1.2, 1.7 s, each column from the nearest seed. From about 0.4 s the
# dashed V0 = 80 curve lies on it.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_curve", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_curve.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

CFG = {"x_anchor": ("left", 0.0, 0.2), "y_anchor": ("bottom", 0.0, 20.0), "open": 9, "pick": "trace",
       "seed": [(0.1, "bottom"), (0.7, "only"), (1.2, "only"), (1.7, "only")]}

def read(image, at):
    return C.read_curve(image, at, CFG)
