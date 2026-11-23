"""Fig 8j (PDF p. 17): threshold division strain against cell node number (S2 Table set).

One orange-red curve. Axis labels matched: x 10, 20, 30, 40 (0 at the corner),
y 0.55 ... 0.7 (0.5 at the corner). Reader: _panel.py in this folder.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("bagchi2025_panel", os.path.join(os.path.dirname(__file__), "_panel.py"))
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)


def read(image, at):
    cal = P.calibrate(image, [10, 20, 30, 40], [0.55, 0.6, 0.65, 0.7], x_corner=0, y_corner=0.5)
    mask = P.hue_mask(image, 0, 40)
    return P.read_curve(image, at, cal, mask, seed=(5, 0.67))
