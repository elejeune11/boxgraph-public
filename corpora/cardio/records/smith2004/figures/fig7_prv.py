# Fig. 7 (p. 8), bottom-right panel: P_rv, the second curve from the top at t = 0.15 s and
# 0.45 s (rising, then the falling curve the label 'P_rv' points to). Calibration as
# fig7_ppa: frame left = 0 s, gridlines every 0.5 s; dotted top edge = 30 mmHg, gridlines
# every 10 mmHg. Traced from the second run at t = 0.15, 0.45 s and 0.75 s later in the
# second beat, each column from the nearest seed; where P_rv merges with P_pa (ejection)
# the merged run's extent is the interval. Positions where it runs along P_vc in late
# filling (about 0.75-0.85 s) are not read.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_curve", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_curve.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

CFG = {"x_anchor": ("left", 0.0, 0.5), "y_anchor": ("top", 30.0, 10.0), "lattice_tol": 0.04,
       "open": 6, "pick": "trace", "seed": [(0.15, "second"), (0.45, "second"), (0.6, "bottom"), (0.9, "second"), (1.2, "second"), (1.35, "bottom")]}


def read(image, at):
    return C.read_curve(image, at, CFG)
