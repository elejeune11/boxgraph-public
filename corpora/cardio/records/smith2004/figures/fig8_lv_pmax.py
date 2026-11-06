# Fig. 8 (p. 8), left-ventricle panel: the tops of the two left-ventricle loops: the higher belongs to the larger loop (P_th = -4), whose right side the -4 mmHg arrow marks.
# Calibration: frame left = 50 ml, gridlines every 20 ml (labels 50 ... 150); dotted/solid top = 140 mmHg, gridlines every 20 mmHg.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_loops", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_loops.py"))
L = importlib.util.module_from_spec(_s)
_s.loader.exec_module(L)

CFG = {"x_anchor": ("left", 50.0, 20.0), "y_anchor": ("top", 140.0, 20.0), "open": 13, "disk": True, "ink_thr": 200, "frame_mode": "frac", "feature": "peaks", "n": 2, "order": [-4, 0]}

def read(image, at):
    return L.read_loops(image, at, CFG)
