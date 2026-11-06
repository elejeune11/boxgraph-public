"""Fig. 5(a) (p. 7): P(sat), the dash-dot-dot line: the middle one of the three dashed tracks; see _fig5.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig5", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig5.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_dash_track(image, at, "a", 1, 3)
