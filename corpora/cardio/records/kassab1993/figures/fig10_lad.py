"""Fig. 10 (p. 12), total cross-sectional area: the LAD (open triangles) points, at the orders given in `at`. Method and intervals: _kassab.py;
axis labels and legend boxes: _fig10.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig10", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig10.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read(image, at, "triangle")
