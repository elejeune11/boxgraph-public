"""Fig. 6 (p. 10): mean element diameter (um, log axis, labels 10000 to 1) against order (1-11).
The order-1 tick sits on the y axis and the lowest label (1) on the x axis. Legend glyphs: the
crop boxes below (pixels of the 1200 dpi crop). Method: see _kassab.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kassab", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kassab.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

CFG = {
    "y_log": True,
    "y_labels": [10000, 1000, 100, 10, 1],
    "y_major": 35,
    "y_bottom_at_axis": True,
    "x_orders": list(range(1, 12)),
    "x_major": 15,
    "x_first_at_axis": True,
    "legend_area": (2640, 1180, 3400, 1720),
    "legend": {"square": (2660, 1190, 2850, 1340), "triangle": (2660, 1350, 2850, 1500), "circle": (2660, 1510, 2850, 1690)},
}


def read(image, at, series):
    return K.read(image, at, CFG, series)
