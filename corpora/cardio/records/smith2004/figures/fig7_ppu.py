# Fig. 7 (p. 8), bottom-left panel: P_pu, the lowest curve at t = 0.4 s, when P_lv is high
# (the nearly flat line the label 'P_pu' points to). Calibration as fig7_pao: frame left =
# 0 s, gridlines every 0.5 s; dotted top edge = 150 mmHg, gridlines every 50 mmHg. Traced
# from t = 0.4 s; where P_lv crosses or runs along it, the merged run's extent is the interval.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_curve", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_curve.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

CFG = {"x_anchor": ("left", 0.0, 0.5), "y_anchor": ("top", 150.0, 50.0), "lattice_tol": 0.04,
       "open": 6, "pick": "trace", "seed": [(0.2, "bottom"), (0.4, "bottom"), (0.55, "bottom"), (0.6, "second_bottom"), (0.7, "second_bottom"), (0.95, "bottom"), (1.15, "bottom"), (1.3, "bottom"), (1.35, "second_bottom"), (1.45, "second_bottom")]}


def read(image, at):
    return C.read_curve(image, at, CFG)
