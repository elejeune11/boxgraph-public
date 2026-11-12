"""Fig. 1A (PDF p. 5): the red bars (HFpEF), % of patients per bin of heart weight at autopsy.
Each red bar stands right of its x tick. Read by the shared code in _kit.py (histogram):
axes calibrated on their tick marks, each bar read at its top edge."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kit", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

YLABELS = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0]   # y tick labels as printed
XLABELS = [150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0, 650.0, 700.0, 750.0, 800.0, 850.0]   # x tick labels as printed, left to right


def read(image, at):
    return K.histogram(image, at, YLABELS, XLABELS, 'red', 'right')
