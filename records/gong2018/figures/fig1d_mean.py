"""Fig. 1D (PDF p. 3): spreading speed vs time for the typical parameter set of the
caption (ka = 1 pN/nm, kl = 0.1 pN/nm, eta = 1 pN s/nm); the black dash-dotted line
is the mean spreading speed over one cycle (caption).  Read by _dashdot.py (see its
docstring).  The x of the reading is the viscosity of the caption, eta = 1 pN s/nm,
so the datum is indexed by viscosity.  Axes: x 0 to 30 s from the ticks on the top
spine, y 0 to 100 nm/s from the ticks on the right spine (the traces cross the
left and bottom spines).
"""
import importlib.util
from pathlib import Path

AXES = {
    "tick_px": 16,
    "margin": 50,  # the tick marks here are about 40 px long
    "x": {"labels": [0, 10, 20, 30], "edge_ticks": ["start", "end"], "band": "top"},
    "y": {"labels": [100, 80, 60, 40, 20, 0], "edge_ticks": ["start", "end"], "band": "right"},
}
SERIES = [
    {"x": 1.0, "what": "black, the typical set (eta = 1)", "color": [0, 0, 0], "tol": 120, "max_h": 16},
]
# the labels "Vs" and "t_life" and the t_life arrow
EXCLUDE = [[1300, 550, 1650, 750], [650, 1700, 2000, 2150]]


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_dashdot", Path(__file__).with_name("_dashdot.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_lines(image, AXES, SERIES, EXCLUDE)
