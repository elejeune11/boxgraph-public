"""Fig. 3c (p. 6): the three grey filled circles (solver time, right axis). See _fig3c.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig3c", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig3c.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_points(image, "grey")
