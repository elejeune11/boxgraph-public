"""Fig 8l (PDF p. 17): cell damping constant against cell node number (S2 Table set).

One purple curve. Axis labels matched: x 10, 20, 30, 40 (0 at the corner),
y 0.55, 0.66, 0.77, 0.88 (0.44 at the corner). Reader: _panel.py in this folder.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("bagchi2025_panel", os.path.join(os.path.dirname(__file__), "_panel.py"))
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)


def read(image, at):
    cal = P.calibrate(image, [10, 20, 30, 40], [0.55, 0.66, 0.77, 0.88], x_corner=0, y_corner=0.44)
    mask = P.hue_mask(image, 255, 320, smin=30)
    return P.read_curve(image, at, cal, mask, seed=(10, 0.7))
