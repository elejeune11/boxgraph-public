"""Fig. 2A (PDF p. 6): the red bars (HFpEF), % of patients per bin of total MVD.
Each red bar stands right of its x tick. Read by the shared code in _kit.py (histogram):
axes calibrated on their tick marks, each bar read at its top edge."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kit", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

YLABELS = [0.0, 10.0, 20.0, 30.0, 40.0]   # y tick labels as printed
XLABELS = [100.0, 300.0, 500.0, 700.0, 900.0, 1100.0, 1300.0, 1500.0, 1700.0, 1900.0]   # x tick labels as printed, left to right


def read(image, at):
    return K.histogram(image, at, YLABELS, XLABELS, 'red', 'right')
