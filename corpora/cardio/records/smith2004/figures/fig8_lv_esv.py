# Fig. 8 (p. 8), left-ventricle panel: the left (end-systolic) vertical sides of the two left-ventricle loops: the left one (about 62 ml) curves up into the lower arc, which ends on the P_th = 0 right side; the right one belongs to P_th = -4.
# Calibration: frame left = 50 ml, gridlines every 20 ml (labels 50 ... 150); dotted/solid top = 140 mmHg, gridlines every 20 mmHg.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_loops", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_loops.py"))
L = importlib.util.module_from_spec(_s)
_s.loader.exec_module(L)

CFG = {"x_anchor": ("left", 50.0, 20.0), "y_anchor": ("top", 140.0, 20.0), "open": 13, "disk": True, "ink_thr": 200, "frame_mode": "frac", "feature": "left_edges", "n": 2, "order": [0, -4]}

def read(image, at):
    return L.read_loops(image, at, CFG)
