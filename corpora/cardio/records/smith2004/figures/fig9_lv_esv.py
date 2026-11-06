# Fig. 9 (p. 8), left-ventricle panel: the left sides of the three left-ventricle loops, left to right 0.5 x, 1 x, 2 x R_sys.
# Calibration: frame right = 150 ml, gridlines every 50 ml (labels 50, 100, 150); top = 180 mmHg, gridlines every 20 mmHg.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_loops", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_loops.py"))
L = importlib.util.module_from_spec(_s)
_s.loader.exec_module(L)

CFG = {"x_anchor": ("right", 150.0, 50.0), "y_anchor": ("top", 180.0, 20.0), "open": 13, "disk": True, "ink_thr": 200, "frame_mode": "frac", "feature": "left_edges", "n": 3, "order": [0.5, 1, 2]}

def read(image, at):
    return L.read_loops(image, at, CFG)
