"""Fig. 8 (p. 11): S/E, the segments/elements numbers ratio (linear axis, labels 30 to 0), against
order (1-11), with vertical error bars. The order-1 tick sits on the y axis and the lowest label
(0) on the x axis. Legend glyphs: the crop boxes below (pixels of the 1200 dpi crop). Method: see
_kassab.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kassab", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kassab.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

CFG = {
    "y_log": False,
    "y_labels": [30, 25, 20, 15, 10, 5, 0],
    "y_major": 30,
    "y_bottom_at_axis": True,
    "x_orders": list(range(1, 12)),
    "x_major": 15,
    "x_first_at_axis": True,
    "bars": True,
    "legend_area": (780, 140, 1280, 680),
    "legend": {"square": (790, 150, 960, 310), "triangle": (790, 320, 960, 480), "circle": (790, 490, 960, 660)},
}


def read(image, at, series):
    return K.read(image, at, CFG, series)
