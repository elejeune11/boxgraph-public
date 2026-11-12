"""Fig. 4A (PDF p. 7): the bottom edge of the box of each Tukey box (x 1 = Control (black, n = 104), 2 = HFpEF (red, n = 124), 3 = HFrEF (blue, n = 27)).
Read by the shared code in _kit.py (boxes / read_boxes): y calibrated on its tick marks; each box
found as a component of its colour with two wide lines joined by its sides."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kit", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

YLABELS = [0.0, 500.0, 1000.0, 1500.0, 2000.0, 2500.0]   # y tick labels as printed
BOXES = {'1': ('black', 0), '2': ('red', 0), '3': ('blue', 0)}   # x -> (colour, box number of that colour from the left, from 0)


def read(image, at):
    return K.read_boxes(image, at, BOXES, 'q25', YLABELS)
