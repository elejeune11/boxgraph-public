# Fig. 5 (p. 7), bottom panel: P(3), the constant outlet pressure, the upper of the two long
# horizontal lines across the box. Calibration as fig5_p2_v010.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_curve", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_curve.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

CFG = {"x_anchor": ("left", 0.0, 0.2), "y_anchor": ("bottom", 0.0, 20.0), "open": 9, "pick": "hline", "which": "highest"}

def read(image, at):
    return C.read_curve(image, at, CFG)
