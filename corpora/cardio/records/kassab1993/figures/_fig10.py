"""Fig. 10 (p. 12): total cross-sectional area of all elements of an order (cm2, linear axis,
labels 0.5 to 0.0) against order, the order axis reversed (11 at the left, on the y axis, to 1 at
the right), with vertical error bars. The lowest label (0.0) sits on the x axis. Legend glyphs: the
crop boxes below (pixels of the 1200 dpi crop). Method: see _kassab.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kassab", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kassab.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

CFG = {
    "y_log": False,
    "y_labels": [0.5, 0.4, 0.3, 0.2, 0.1, 0.0],
    "y_major": 30,
    "y_bottom_at_axis": True,
    "x_orders": list(range(11, 0, -1)),
    "x_major": 15,
    "x_first_at_axis": True,
    "bars": True,
    "legend_area": (780, 180, 1300, 730),
    "legend": {"square": (800, 200, 950, 340), "triangle": (800, 380, 950, 520), "circle": (800, 570, 950, 710)},
}


def read(image, at, series):
    return K.read(image, at, CFG, series)
