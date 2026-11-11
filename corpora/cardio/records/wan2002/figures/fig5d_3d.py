"""Fig. 5 D - Outlet Flow (PDF p. 10): the solid line (3D FEM, as the legend says) of panel D - Outlet Flow. Code in _wan.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_wan", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_wan.py"))
_w = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_w)

X = [0, 0.1, 0.2, 0.3, 0.4]      # printed x tick labels, left to right
YL = [140, 120, 100, 80, 60, 40, 20, 0]    # printed left-axis tick labels, top to bottom
YR = None    # printed right-axis tick labels, top to bottom (None: no right scale used)


def read(image, at):
    cal = _w.calibrate(image, X, YL, YR, dpi=1200)
    return _w.read_curve(image, at, cal, "solid", "left")
