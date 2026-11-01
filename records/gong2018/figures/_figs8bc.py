"""Fig. S8B and S8C, left panels, of gong2018 (PDF p. 19): spreading velocity from
three simulations, as bars: "Elastic" (dark grey), "Effective timescale" (orange)
and "Multiple timescales" (dark orange).  The categories are not numbers: the x of
each reading is the bar's position from the left (0, 1, 2), as the labels under
the bars name them.  Read by _bars.py (see its docstring): y from the outward
ticks of the y axis, 20 to 120 nm/s.
"""
import importlib.util
from pathlib import Path

AXIS = {"y_labels": [120, 100, 80, 60, 40, 20], "ticks": "out", "tick_len": 16, "axis_max_col": 950,
        "src_px": 8}
BARS = [
    {"categories": [0], "color": [56, 54, 54], "tol": 40},     # Elastic
    {"categories": [1], "color": [236, 125, 50], "tol": 30},   # Effective timescale
    {"categories": [2], "color": [197, 90, 17], "tol": 30},    # Multiple timescales
]


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_bars", Path(__file__).with_name("_bars.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = []
    for b in BARS:
        out += mod.read_bars(image, {**AXIS, **b})
    return out
