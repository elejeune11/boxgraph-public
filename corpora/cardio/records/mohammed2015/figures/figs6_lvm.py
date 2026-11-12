"""Fig. S6 (PDF p. 25): every black marker, LV mass (g) against microvessel density, HFpEF patients.
Read by the shared code in _kit.py (scatter): axes calibrated on their tick marks, overlapping
markers separated by fitting discs of the marker radius. The red regression line and the r/p text
are not read."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kit", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

XLABELS = [400.0, 800.0, 1200.0, 1600.0]   # x tick labels as printed
YLABELS = [0.0, 100.0, 200.0, 300.0, 400.0, 500.0]   # y tick labels as printed


def read(image, at):
    return K.scatter(image, XLABELS, YLABELS)
