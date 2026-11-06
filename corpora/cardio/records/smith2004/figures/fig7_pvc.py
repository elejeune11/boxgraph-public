# Fig. 7 (p. 8), bottom-right panel: P_vc, the lowest curve at t = 0.3 s, when P_rv is
# high (the nearly flat line the label 'P_vc' points to). Calibration as fig7_ppa: frame
# left = 0 s, gridlines every 0.5 s; dotted top edge = 30 mmHg, gridlines every 10 mmHg.
# Traced (one seed per beat, the second 0.75 s later) from t = 0.3 s; where P_rv crosses or runs along it, the merged run's extent is
# the interval.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_curve", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_curve.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

CFG = {"x_anchor": ("left", 0.0, 0.5), "y_anchor": ("top", 30.0, 10.0), "lattice_tol": 0.04,
       "open": 6, "pick": "trace", "seed": [(0.3, "bottom"), (0.65, "second_bottom"), (1.05, "bottom"), (1.4, "second_bottom")]}


def read(image, at):
    return C.read_curve(image, at, CFG)
