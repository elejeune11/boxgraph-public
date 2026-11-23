"""Fig 11k (PDF p. 21): substrate stiffness against substrate node index, five
straight lines labelled 1-5 in the legend (red, orange, green, blue, purple).
Axis labels matched: x 0, 50, 100, 150, 200 and y 0, 5, 10, 15 (both axes start
before 0, no label at the corner). The legend's line samples are blanked.
Reader: _panel.py in this folder."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("bagchi2025_panel", os.path.join(os.path.dirname(__file__), "_panel.py"))
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)

LINES = {   # hue range, least saturation, seed (x, y)
    1: (345, 8, 80, (20, 1.4)),
    2: (12, 35, 80, (20, 2.5)),
    3: (80, 150, 60, (20, 3.8)),
    4: (210, 250, 40, (20, 6.85)),
    5: (260, 310, 40, (20, 9.6)),
}


def read_curve(image, at, k):
    cal = P.calibrate(image, [0, 50, 100, 150, 200], [0, 5, 10, 15])
    lo, hi, smin, seed = LINES[k]
    mask = P.hue_mask(image, lo, hi, smin=smin)
    return P.read_curve(image, at, cal, mask, seed=seed, legend=(140, 200, -1.5, 6.5))
