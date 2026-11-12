"""Fig. 3A (PDF p. 6): the black bars (Control), % of patients per bin of % area fibrosis.
Each black bar stands left of its x tick. Read by the shared code in _kit.py (histogram):
axes calibrated on their tick marks, each bar read at its top edge."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kit", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

YLABELS = [0.0, 25.0, 50.0]   # y tick labels as printed
XLABELS = [0.0, 4.0, 8.0, 12.0, 16.0, 20.0, 24.0, 28.0, 32.0, 36.0, 40.0]   # x tick labels as printed, left to right


def read(image, at):
    return K.histogram(image, at, YLABELS, XLABELS, 'black', 'left')
