"""Fig. S4 (PDF p. 52): the red curve, the two-term exponential (Eq. 4) fitted to the integrin-
fibronectin dissociation rates, k_off against force F.

Shared code in _hd.py. x: linear, the long ticks 0, 15, 30, 45 pN (the y axis stands a little
left of 0); y: log, the long ticks 0.1, 1, 10 s^-1. Vector figure. The curve: the red pixels;
where a symbol is drawn over it the curve is hidden, and such positions are not used.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_hd", Path(__file__).with_name("_hd.py"))
H = importlib.util.module_from_spec(_s)
_s.loader.exec_module(H)

SPEC = {
    "x": {"marks": [(0, 0), (1, 15), (2, 30), (3, 45)], "major": 0.8},
    "y": {"scale": "log10", "marks": [(0, 0.1), (1, 1), (2, 10)], "major": 0.8},
}


def read(image, at):
    cal = H.calibrate(image, SPEC)
    sp = cal["sp"]
    box = (sp["c1"] + 2, 0, image.shape[1], sp["r0"] - 1)
    return H.curve(image, (240, 20, 20), 80, cal["x"], cal["y"], at, box, pick="top")
