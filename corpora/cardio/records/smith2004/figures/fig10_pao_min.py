# Fig. 10 (p. 9), the aortic pressure plot: the lowest point of each aortic pressure curve, top curve first: 2 x, 1 x, 0.5 x R_sys (labelled).
# Calibration: lowest gridline = 40 mmHg, every 20 mmHg (labels 40 ... 160); the time axis has no ticks and is not used.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_loops", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_loops.py"))
L = importlib.util.module_from_spec(_s)
_s.loader.exec_module(L)

CFG = {"y_anchor": ("gridlow", 40.0, 20.0), "open_top": True, "open": 13, "disk": True, "ink_thr": 200, "frame_mode": "frac", "feature": "curve_min", "order": [2, 1, 0.5]}

def read(image, at):
    return L.read_loops(image, at, CFG)
