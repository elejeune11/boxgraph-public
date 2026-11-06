# Fig. 5 (p. 7), bottom panel: chamber pressure P(2) of the single-chamber model, the solid
# curve (V0 = 10 ml). Calibration: solid left axis = 0 s, gridlines every 0.2 s; solid bottom
# axis = 0 mmHg, gridlines every 20 mmHg (labels 0 ... 140). The long horizontal lines P(1),
# P(3) cross it; where they merge with it the merged run is the interval. Traced from the
# lowest run at t = 0.1, 0.7, 1.4 s and the middle one (between P(3) and P(1)) at 1.75 s,
# each column from the nearest seed.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_curve", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_curve.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

CFG = {"x_anchor": ("left", 0.0, 0.2), "y_anchor": ("bottom", 0.0, 20.0), "open": 9, "pick": "trace",
       "seed": [(0.1, "bottom"), (0.7, "bottom"), (1.4, "bottom"), (1.75, "second")]}


def read(image, at):
    return C.read_curve(image, at, CFG)
