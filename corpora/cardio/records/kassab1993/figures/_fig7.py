"""Fig. 7 (p. 10): mean element length (um, log axis, labels 100000 to 100) against order (1-11),
with vertical error bars. The order-1 tick sits on the y axis and the lowest label (100) on the
x axis. Legend glyphs: the crop boxes below (pixels of the 1200 dpi crop). Method: see _kassab.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kassab", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kassab.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

CFG = {
    "y_log": True,
    "y_labels": [100000, 10000, 1000, 100],
    "y_major": 35,
    "y_bottom_at_axis": True,
    "x_orders": list(range(1, 12)),
    "x_major": 15,
    "x_first_at_axis": True,
    "bars": True,
    "legend_area": (2760, 1190, 3400, 1720),
    "legend": {"square": (2780, 1210, 2950, 1360), "triangle": (2780, 1380, 2950, 1530), "circle": (2780, 1540, 2950, 1710)},
}


def read(image, at, series):
    return K.read(image, at, CFG, series)
