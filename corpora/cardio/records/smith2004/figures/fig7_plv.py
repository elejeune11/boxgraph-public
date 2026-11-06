# Fig. 7 (p. 8), bottom-left panel: P_lv, the second curve from the top at t = 0.2 s and
# 0.45 s (rising, then the falling curve the label 'P_lv' points to). Calibration as
# fig7_pao: frame left = 0 s, gridlines every 0.5 s; dotted top edge = 150 mmHg, gridlines
# every 50 mmHg. Traced from the second run at t = 0.2, 0.45 s and 0.75 s later in the
# second beat, each column from the nearest seed; where P_lv merges with P_ao (ejection)
# the merged run's extent is the interval. Positions where it runs along P_pu in late
# filling (about 0.75-0.9 s) are not read.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_curve", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_curve.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

CFG = {"x_anchor": ("left", 0.0, 0.5), "y_anchor": ("top", 150.0, 50.0), "lattice_tol": 0.04,
       "open": 6, "pick": "trace", "seed": [(0.2, "second"), (0.3, "top"), (0.45, "second"), (0.95, "second"), (1.05, "top"), (1.2, "second")]}


def read(image, at):
    return C.read_curve(image, at, CFG)
