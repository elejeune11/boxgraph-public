# Fig. 5 (p. 7), bottom panel: chamber pressure P(2) of the single-chamber model, the dashed
# curve (V0 = 80 ml): its peak only. Calibration as fig5_p2_v010. The seed is the highest
# run of thick ink within 60 columns of t = 0.3 s (the dash at the top of the peak; the
# solid curve and P(3) lie below it); the dash is traced to either side. The rest of the
# dashed curve is not read: on its steep rise and fall the trace cannot bridge the gaps,
# and the 'V0=80' label and arrow lie against it.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_curve", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_curve.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

CFG = {"x_anchor": ("left", 0.0, 0.2), "y_anchor": ("bottom", 0.0, 20.0), "open": 9, "pick": "trace",
       "seed": [(0.3, "top")], "seed_window": 60}


def read(image, at):
    return C.read_curve(image, at, CFG)
