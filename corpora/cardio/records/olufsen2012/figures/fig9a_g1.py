"""Fig. 9 (left) (PDF p. 18): the solid cyan curve, gamma = 1.0. Code in _fig89.py and _common.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig89", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig89.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read(image, at, "9a", "cyan")
