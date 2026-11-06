"""Fig. 4 (phase): the crosses (measured on the model) (shared code in _imp.py)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_imp", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_imp.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)

X_LABELS = [0, 2, 4, 6, 8, 10, 12, 14]  # printed frequency labels matched to the ticks found under the axis
Y_LABELS = [-50, 0, 50]  # printed ordinate labels (and the unlabelled ticks between), bottom to top
IGNORE = [[1000, 1400, 1950, 1650]]  # boxes around the panel's text (title, unit, words), not data


def read(image, at):
    A = _f.analyse(image, X_LABELS, Y_LABELS, phase=True, rings=True, ignore=IGNORE)
    return _f.read_crosses(A)
