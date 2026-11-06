"""Fig. 10 (lower right, gamma = 1.00) (PDF p. 19): the solid curve (blue), xi = 2.2: simulated flow in the femoral artery, read where the five curves are apart. Code in _wave.py and _common.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_wave", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_wave.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read(image, at, "10", "blue", half_window=12)
