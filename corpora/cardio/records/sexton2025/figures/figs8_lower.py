"""Fig. S8 (p. 51): the lower dark red line (a convex domain) with its +-1 SD bars. See _figs8.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_figs8", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_figs8.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read(image, at, "lower")
