"""Fig. 11 (lower right, gamma = 1.00) (PDF p. 20): the dash-dot-dot curve (purple), xi = 3.0: simulated pressure in the main pulmonary artery. Code in _wave.py and _common.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_wave", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_wave.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read(image, at, "11", "purple", half_window=30)
