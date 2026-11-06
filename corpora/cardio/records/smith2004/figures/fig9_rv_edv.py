# Fig. 9 (p. 8), right-ventricle panel: the right sides of the three right-ventricle loops, left to right 2 x, 1 x, 0.5 x R_sys (labelled arrows).
# Calibration: frame right = 140 ml, gridlines every 20 ml (labels 60 ... 140); top = 180 mmHg, gridlines every 20 mmHg.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_loops", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_loops.py"))
L = importlib.util.module_from_spec(_s)
_s.loader.exec_module(L)

CFG = {"x_anchor": ("right", 140.0, 20.0), "y_anchor": ("top", 180.0, 20.0), "open": 13, "disk": True, "edge_band": (-2, 15), "min_len_frac": 0.3, "ink_thr": 200, "frame_mode": "frac", "feature": "right_edges", "n": 3, "order": [2, 1, 0.5]}

def read(image, at):
    return L.read_loops(image, at, CFG)
