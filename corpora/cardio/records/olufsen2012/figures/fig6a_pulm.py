"""Fig. 6(a), right (PDF p. 16): the simulated flow in the main pulmonary artery (blue curve) over one period. Code in _wave.py and _common.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_wave", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_wave.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read(image, at, "6a_pulm", "blue", half_window=12)
