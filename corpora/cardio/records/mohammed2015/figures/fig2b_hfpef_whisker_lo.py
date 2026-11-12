"""Fig. 2B (PDF p. 6): the lower whisker end (cap) of each Tukey box (the red (HFpEF) boxes; x 1 = Epi, 2 = Midwall, 3 = Endo, 4 = Pap).
Read by the shared code in _kit.py (boxes / read_boxes): y calibrated on its tick marks; each box
found as a component of its colour with two wide lines joined by its sides."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kit", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

YLABELS = [0.0, 1000.0, 2000.0, 3000.0]   # y tick labels as printed
BOXES = {'1': ('red', 0), '2': ('red', 1), '3': ('red', 2), '4': ('red', 3)}   # x -> (colour, box number of that colour from the left, from 0)


def read(image, at):
    return K.read_boxes(image, at, BOXES, 'whisker_lo', YLABELS)
