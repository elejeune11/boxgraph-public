"""Fig. 9 (p. 12): total number of elements (log axis, labels 10^6 to 10^0) against order (1-11),
with vertical error bars. The order-1 tick sits on the y axis and the lowest label (10^0) on the
x axis. Legend glyphs: the crop boxes below (pixels of the 1200 dpi crop). Method: see _kassab.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kassab", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kassab.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

CFG = {
    "y_log": True,
    "y_labels": [1e6, 1e5, 1e4, 1e3, 1e2, 1e1, 1e0],
    "y_major": 35,
    "y_bottom_at_axis": True,
    "x_orders": list(range(1, 12)),
    "x_major": 15,
    "x_first_at_axis": True,
    "bars": True,
    "legend_area": (2460, 500, 2960, 1020),
    "legend": {"square": (2480, 515, 2630, 660), "triangle": (2480, 700, 2630, 840), "circle": (2480, 870, 2630, 1010)},
}


def read(image, at, series):
    return K.read(image, at, CFG, series)
