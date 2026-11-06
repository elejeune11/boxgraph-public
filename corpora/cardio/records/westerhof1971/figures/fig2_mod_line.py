"""Fig. 2 (modulus): the fully drawn line (the measured input impedance of the hydraulic model) (shared code in _imp.py)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_imp", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_imp.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)

X_LABELS = [0, 2, 4, 6, 8, 10, 12, 14]  # printed frequency labels matched to the ticks found under the axis
Y_LABELS = [0, 200, 400, 600, 800]  # printed ordinate labels (and the unlabelled ticks between), bottom to top
IGNORE = [[780, 200, 1430, 550], [2050, 3240, 3280, 3460]]  # boxes around the panel's text (title, unit, words), not data


def read(image, at):
    A = _f.analyse(image, X_LABELS, Y_LABELS, phase=False, rings=False, ignore=IGNORE)
    return _f.read_line(A, at)
