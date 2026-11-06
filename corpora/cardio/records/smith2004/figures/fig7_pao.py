# Fig. 7 (p. 8), bottom-left panel: P_ao, the curve that is uppermost at t = 0.05 s (the
# label 'P_ao' points to it). Calibration: frame left = 0 s, gridlines every 0.5 s; the top
# edge of the box (a dotted line) is 150 mmHg, gridlines every 50 mmHg (labels 0, 50,
# 100, 150); the solid bottom axis lies below 0 and is not a labelled line. Traced from
# the top run at t = 0.05 s and, for the second beat, at t = 1.45 s; where P_ao and P_lv
# merge into one run, its extent is the interval.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_curve", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_curve.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

CFG = {"x_anchor": ("left", 0.0, 0.5), "y_anchor": ("top", 150.0, 50.0), "lattice_tol": 0.04,
       "open": 6, "pick": "trace", "seed": [(0.05, "top"), (0.35, "second"), (0.4, "top"), (0.45, "top"), (0.55, "top"), (1.1, "second"), (1.15, "top"), (1.2, "top"), (1.3, "top")]}


def read(image, at):
    return C.read_curve(image, at, CFG)
