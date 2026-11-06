"""Fig. S3D of gong2018 (PDF p. 16): mean spreading speed vs viscosity without
reinforcement, kl = 0.1 pN/nm, four ka.  Each series is a thick solid line through
its markers; the lines are read (not the markers, which overlap at low viscosity)
by _lines.py at the reader's chosen viscosities.  Where a line is hidden under the
line drawn on top of it (low viscosity: the blue line covers the others) or runs
steeply (the drops of the red and green curves) the position is not read.
Axes: inward ticks on the bottom spine (0.1, 1, 10; 0.01 and 100 at the left
and right spines, one decade apart from their neighbours) and on the left spine (0 at the bottom spine, 20, 40, 60, 80).
"""
import importlib.util
from pathlib import Path

AXES = {
    "tick_px": 16,
    "dark": 150,  # the spines and ticks are grey (about 85-120)
    "x": {"labels": [0.01, 0.1, 1, 10, 100], "scale": "log10", "edge_ticks": ["start", "end"], "band": "bottom"},
    "y": {"labels": [80, 60, 40, 20, 0], "edge_ticks": ["end"], "band": "left"},
}
SERIES = {
    "ka01": {"color": [0, 0, 255], "tol": 110},
    "ka05": {"color": [150, 45, 10], "tol": 70},
    "ka2": {"color": [0, 128, 0], "tol": 80},
    "ka10": {"color": [255, 0, 0], "tol": 110},
}
# an uncovered line is 18-24 rows thick
COMMON = {"open_r": 5, "max_run": 40, "min_run": 17, "half": 2, "src_px": 8, "margin": 20}


def read(image, at, key):
    spec = importlib.util.spec_from_file_location("gong2018_lines", Path(__file__).with_name("_lines.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, AXES, {**COMMON, **SERIES[key]})
