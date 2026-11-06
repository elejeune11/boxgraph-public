# Fig. 7 (p. 8), bottom-right panel: P_pa, the curve that is uppermost at t = 0.05 s (the
# label 'P_pa' points to it). Calibration: frame left = 0 s, gridlines every 0.5 s; the
# dotted top edge of the box is 30 mmHg, gridlines every 10 mmHg (labels 0 ... 30); the
# solid bottom axis lies at about -5 and is not a labelled line. Traced from t = 0.05 s;
# during ejection P_pa and P_rv merge, and the merged run's extent is the interval.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_curve", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_curve.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

CFG = {"x_anchor": ("left", 0.0, 0.5), "y_anchor": ("top", 30.0, 10.0), "lattice_tol": 0.04,
       "open": 6, "pick": "trace", "seed": [(0.05, "top"), (0.3, "second"), (0.45, "top"), (0.85, "top"), (1.05, "second"), (1.3, "top")]}


def read(image, at):
    return C.read_curve(image, at, CFG)
