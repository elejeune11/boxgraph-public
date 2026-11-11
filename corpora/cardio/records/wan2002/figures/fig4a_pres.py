"""Fig. 4 A - Inlet (PDF p. 9): the dashed line (pressure, right axis) of panel A - Inlet. Code in _wan.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_wan", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_wan.py"))
_w = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_w)

X = [0, 0.2, 0.4, 0.6, 0.8]      # printed x tick labels, left to right
YL = [100, 90, 80, 70, 60, 50, 40, 30]    # printed left-axis tick labels, top to bottom
YR = [120, 115, 110, 105, 100, 95, 90, 85]    # printed right-axis tick labels, top to bottom (None: no right scale used)


def read(image, at):
    cal = _w.calibrate(image, X, YL, YR, dpi=2000)
    return _w.read_curve(image, at, cal, "dashed", "right", hidden_ok=True)
