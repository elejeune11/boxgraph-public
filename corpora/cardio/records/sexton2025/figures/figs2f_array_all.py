"""Fig. S2F (p. 39): collision detection time, array, all collisions (orange mean line). See _figs2.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_figs2", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_figs2.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_line(image, at, "f_array_all")
