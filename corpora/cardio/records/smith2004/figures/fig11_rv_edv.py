# Fig. 11 (p. 9), right-ventricle panel: the right side of each right-ventricle loop, in its own colour.
# Calibration: frame left = 20 ml, gridlines every 20 ml (labels 20 ... 140); top = 200 mmHg, gridlines every 20 mmHg.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_loops", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_loops.py"))
L = importlib.util.module_from_spec(_s)
_s.loader.exec_module(L)

CFG = {"x_anchor": ("left", 20.0, 20.0), "y_anchor": ("top", 200.0, 20.0), "min_len_frac": 0.03, "ink_thr": 200, "frame_mode": "frac", "feature": "right_edges", "colors": {0.5: "magenta", 1.0: "blue", 2.0: "red"}}

def read(image, at):
    return L.read_loops(image, at, CFG)
