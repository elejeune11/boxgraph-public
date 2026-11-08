"""Fig. 11 (p. 13): blood volume of all elements of an order (ml, log axis, labels 1 to .0001)
against order, the order axis reversed (11 at the left, on the y axis, to 1 at the right), with
vertical error bars. The lowest label (.0001) sits on the x axis. Legend glyphs: the crop boxes
below (pixels of the 1200 dpi crop). Method: see _kassab.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kassab", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kassab.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

CFG = {
    "y_log": True,
    "y_labels": [1, 0.1, 0.01, 0.001, 0.0001],
    "y_major": 35,
    "y_bottom_at_axis": True,
    "x_orders": list(range(11, 0, -1)),
    "x_major": 15,
    "x_first_at_axis": True,
    "bars": True,
    "legend_area": (740, 1300, 1300, 1850),
    "legend": {"square": (760, 1320, 910, 1470), "triangle": (760, 1500, 910, 1670), "circle": (750, 1690, 910, 1840)},
}


def read(image, at, series):
    return K.read(image, at, CFG, series)
