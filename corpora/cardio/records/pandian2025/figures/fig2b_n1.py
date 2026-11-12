"""Fig. 2b (p. 5): the light grey line (Network-1). See _fig2b.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig2b", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig2b.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_curve(image, at, "n1")
