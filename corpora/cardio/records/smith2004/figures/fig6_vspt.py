# Fig. 6 (p. 7): septum free-wall volume V_spt against time, one purple curve (raster
# image). Calibration: frame left = 0.2 s with gridlines every 0.2 s (labels 0.2 ... 1.2);
# frame bottom = 3.5 ml with gridlines every 0.5 ml (labels 3.5 ... 7). Traced from the
# only run of thick ink at t = 0.3 s and t = 1.05 s, each column from the nearest seed;
# the opening (9 px) removes the dots of the gridlines, the curve is about 24 px thick, and
# a run split by a gap under 9 px (a seam in the raster image) is taken as one.
import importlib.util
import os

_s = importlib.util.spec_from_file_location("_curve", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_curve.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)

CFG = {"x_anchor": ("left", 0.2, 0.2), "y_anchor": ("bottom", 3.5, 0.5), "open": 9, "pick": "trace", "join_gap": 9,
       "seed": [(0.3, "only"), (1.05, "only")]}


def read(image, at):
    return C.read_curve(image, at, CFG)
