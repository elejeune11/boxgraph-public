"""Fig 10k (PDF p. 20): node binding probability against collagen node index, six
curves labelled 1-6 in the legend (red, orange, green, cyan, dark blue, purple).
Axis labels matched: x 0, 50, 100, 150 (the y axis is left of 0), y 0.2 ... 1
(0 at the corner). The legend's line samples are blanked. Each curve is traced
from two seeds, left and right of the point where all six cross.
Reader: _panel.py in this folder."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("bagchi2025_panel", os.path.join(os.path.dirname(__file__), "_panel.py"))
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)

CURVES = {   # hue range, least saturation, seeds (x, y) left and right of the crossing
    1: (345, 8, 80, [(20, 0.95), (110, 0.07)]),
    2: (12, 35, 80, [(20, 0.88), (110, 0.13)]),
    3: (80, 150, 60, [(20, 0.77), (110, 0.25)]),
    4: (170, 200, 60, [(20, 0.665), (110, 0.35)]),
    5: (210, 250, 40, [(20, 0.60), (110, 0.41)]),
    6: (260, 310, 40, [(20, 0.55), (110, 0.455)]),
}


def read_curve(image, at, k):
    cal = P.calibrate(image, [0, 50, 100, 150], [0.2, 0.4, 0.6, 0.8, 1], x_corner=None, y_corner=0)
    lo, hi, smin, seeds = CURVES[k]
    mask = P.hue_mask(image, lo, hi, smin=smin)
    return P.read_curve(image, at, cal, mask, seed=seeds, legend=(118, 152, 0.58, 0.97))
