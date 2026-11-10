"""Fig. S11C (p. 60): parabolic fit of the Bottom channel's velocity profile (blue line). See _figs11c.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_figs11c", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_figs11c.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read(image, at, "bottom")
