"""Fig. 9(B) and 9(C) (PDF p. 9): the solid black structured-tree curve. Code in _common.py.

x axis (log10 omega): the decade ticks are matched, left to right, to the printed labels 10^0, 10^1,
10^2, with the right frame at the label 10^3. y: the frame top and bottom carry the printed end
labels (B: 10^4 and 10^2, log; C: 90 and -90 deg), checked by the major tick between (10^3; 0).
Readings are only requested where the solid line is the only black line (see figures.md).
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)


def read_solid(image, at, ylog, ytop, ybot, ymid):
    cal = _c.calibrate_fig9(image, ylog, ytop, ybot, ymid)
    return _c.read_solid(cal, at)
