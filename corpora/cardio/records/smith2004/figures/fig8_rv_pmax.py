# Fig. 8 (p. 8), right-ventricle panel: the tops of the two right-ventricle loops: the P_th = -4 loop (right) peaks higher (labelled arrows).
# Calibration: lowest vertical gridline = 40 ml, every 20 ml (labels 40 ... 120); top = 140 mmHg, gridlines every 20 mmHg.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_loops", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_loops.py"))
L = importlib.util.module_from_spec(_s)
_s.loader.exec_module(L)

CFG = {"x_anchor": ("gridlow", 40.0, 20.0), "y_anchor": ("top", 140.0, 20.0), "open": 13, "disk": True, "edge_band": (-2, 12), "min_len_frac": 0.3, "ink_thr": 200, "frame_mode": "frac", "feature": "peaks", "n": 2, "order": [-4, 0]}

def read(image, at):
    return L.read_loops(image, at, CFG)
