# Fig. 5 (p. 7), top panel: chamber volume of the single-chamber model, the dashed curve
# (V0 = 80 ml, labelled), on its first rise and plateau (to 0.25 s). Calibration as
# fig5_vol_v010. Traced from the upper curve at t = 0.1 s across the gaps of the dashes
# (up to 60 columns); a position in a gap takes the dashes on either side. The steep
# dashed descent after 0.26 s is not read: the trace cannot bridge its gaps.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_curve", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_curve.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

CFG = {"x_anchor": ("left", 0.0, 0.2), "y_anchor": ("bottom", 0.0, 20.0), "open": 9, "pick": "trace",
       "seed": [(0.1, "top")], "max_skip": 60, "window": 60}


def read(image, at):
    return C.read_curve(image, at, CFG)
