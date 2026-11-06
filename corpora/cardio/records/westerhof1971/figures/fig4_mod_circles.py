"""Fig. 4 (modulus): the circles (measured on the model after addition of the adapter) (shared code in _imp.py)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_imp", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_imp.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)

X_LABELS = [0, 2, 4, 6, 8, 10, 12, 14]  # printed frequency labels matched to the ticks found under the axis
Y_LABELS = [0, 1, 2, 3, 4, 5, 6]  # printed ordinate labels (and the unlabelled ticks between), bottom to top
IGNORE = [[620, 1150, 1300, 1510], [2200, 3040, 2950, 3200]]  # boxes around the panel's text (title, unit, words), not data


def read(image, at):
    A = _f.analyse(image, X_LABELS, Y_LABELS, phase=False, rings=True, ignore=IGNORE)
    return _f.read_circles(A)
