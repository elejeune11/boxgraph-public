"""Fig. S4B (p. 42): partition-of-unity reconstruction time (blue line). See _figs4b.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_figs4b", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_figs4b.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read(image, at, "pu")
