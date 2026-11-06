"""Fig. 3C (PDF p. 5): spreading speed vs time at ka = 1 pN/nm for three viscosities;
the dash-dotted lines are the time averages (caption).  Read by _dashdot.py (see its
docstring).  The x of each reading is the viscosity the legend gives for that
colour: black eta = 10^2, green 10^0 (the dash-dotted green is lighter than the
solid green), red 10^-2 pN s/nm.  Axes: x 0 to 25 s, y 0 to 120 nm/s.
"""
import importlib.util
from pathlib import Path

AXES = {
    "tick_px": 16,
    # ticks on the top and right spines, which no trace crosses
    "x": {"labels": [0, 5, 10, 15, 20, 25], "edge_ticks": ["start", "end"], "band": "top"},
    "y": {"labels": [120, 100, 80, 60, 40, 20, 0], "edge_ticks": ["start", "end"], "band": "right"},
}
SERIES = [
    {"x": 1e-2, "what": "red, eta = 10^-2", "color": [255, 0, 0], "tol": 90, "thick_px": 11, "max_h": 12},
    {"x": 1e0, "what": "light green, eta = 10^0", "color": [115, 180, 75], "tol": 45, "max_h": 12,
     "solid": [0, 125, 0], "thick_px": 11, "grow_px": 6},
    {"x": 1e2, "what": "black, eta = 10^2", "color": [0, 0, 0], "tol": 120, "thick_px": 11, "max_h": 12},
]
# the legend (lines and labels) at the bottom right
EXCLUDE = [[1350, 1300, 2150, 1820]]


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_dashdot", Path(__file__).with_name("_dashdot.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_lines(image, AXES, SERIES, EXCLUDE)
