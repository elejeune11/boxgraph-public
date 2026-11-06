"""Fig. 5 (modulus): the fully drawn line (the theoretical impedance) (shared code in _imp.py)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_imp", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_imp.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)

X_LABELS = [2, 4, 6, 8, 10, 12, 14]  # printed frequency labels matched to the ticks found under the axis
Y_LABELS = [1, 2, 3, 4]  # printed ordinate labels (and the unlabelled ticks between), bottom to top
IGNORE = [[720, 780, 1440, 1160], [2460, 3550, 3390, 3740]]  # boxes around the panel's text (title, unit, words), not data


def read(image, at):
    # neither axis has a tick at its printed 0: the 0s stand where the axes cross
    A = _f.analyse(image, X_LABELS, Y_LABELS, phase=False, rings=True, ignore=IGNORE, zero_at_axes=True)
    return _f.read_line(A, at)
