"""Fig. 1, Pressure (PDF p. 6): the dashed line (outlet): pressure at the outlet. Code in _wan.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_wan", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_wan.py"))
_w = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_w)

X = [0, 0.2, 0.4, 0.6, 0.8, 1.0]      # printed x tick labels, left to right
YL = [200, 180, 160, 140, 120, 100, 80, 60, 40]    # printed left-axis tick labels, top to bottom
YR = None    # printed right-axis tick labels, top to bottom (None: no right scale used)


def read(image, at):
    cal = _w.calibrate(image, X, YL, YR, dpi=1100)
    return _w.read_curve(image, at, cal, "dashed", "left")
