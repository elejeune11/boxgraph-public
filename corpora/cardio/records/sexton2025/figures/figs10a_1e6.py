"""Fig. S10A (p. 58): biventricle, 1E6 vessels (green histogram). See _figs10.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_figs10", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_figs10.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read(image, at, "A", "1e6")
