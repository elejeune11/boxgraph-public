"""Fig. 7(d), left (PDF p. 17): the green dashed upper line, mean pressure along the alpha-branch (window spans the dash gaps). Code in _wave.py and _common.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_wave", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_wave.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read(image, at, "7d_sys", "green", half_window=40)
