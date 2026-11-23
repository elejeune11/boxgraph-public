"""Fig. 5k: fibre recruitment (a.u.), box plots 1-3 = soft (light grey), stiff (black), soft-weld (dark
grey), over the three x ticks. y ticks 0, 2, 4, 6. Each box is the largest connected stroke of its colour
over its tick; its three widest rows are the upper quartile, median and lower quartile, its caps the
whisker ends. See _kit.py (box_plot)."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

BOXES = [((179, 178, 178), 25), ((35, 31, 32), 22), ((79, 75, 76), 22)]
TICKS = [0, 2, 4, 6]


def boxes(image):
    return [K.box_plot(image, rgb, tol, TICKS, i + 1, 3) for i, (rgb, tol) in enumerate(BOXES)]
