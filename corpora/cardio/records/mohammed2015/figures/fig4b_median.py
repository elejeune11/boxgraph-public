"""Fig. 4B (PDF p. 7): the median line of each Tukey box (x 1 = Control (black, n = 104), 2 = HFpEF (red, n = 124), 3 = HFrEF (blue, n = 27)).
Read by the shared code in _kit.py (boxes / read_boxes): y calibrated on its tick marks; each box
found as a component of its colour with two wide lines joined by its sides."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kit", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

YLABELS = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0]   # y tick labels as printed
BOXES = {'1': ('black', 0), '2': ('red', 0), '3': ('blue', 0)}   # x -> (colour, box number of that colour from the left, from 0)


def read(image, at):
    return K.read_boxes(image, at, BOXES, 'median', YLABELS)
