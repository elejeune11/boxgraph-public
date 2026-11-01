"""Fig. S7 of gong2018 (PDF p. 18): spreading speed vs log10 of the stiffness of a
purely elastic substrate; the predicted curve (red line, with reinforcement) and
the speeds extracted from measured spreading areas (black triangle: PA, blue
squares: HA, green circles: alginate), with error bars.

Axes (_axes.py): the x axis is printed as log10(k) on a linear scale, -1 to 1
(the ends at the spines); the readings return k itself (10 to the power of the
calibrated value).  y: 20 to 140 nm/s (ends at the spines).  Ticks on the bottom
and left spines (the curve meets the right spine near 120, the 120 tick is on
the left too).
Markers and error bars by _points.py, the line by _lines.py.
"""
import importlib.util
from pathlib import Path

AXES = {
    "tick_px": 16,
    "x": {"labels": [-1, -0.5, 0, 0.5, 1], "edge_ticks": ["start", "end"], "band": "bottom"},
    "y": {"labels": [140, 120, 100, 80, 60, 40, 20], "edge_ticks": ["start", "end"], "band": "left"},
}
# the legend, top left inside the plot
LEGEND = [[700, 420, 2550, 1060]]
POINTS = {
    # the black caps are thick: a wider opening; the triangle's column from its bar
    "pa": {"color": [0, 0, 0], "tol": 110, "open_r": 14, "min_area": 600, "center_px": 6, "x_from_bar": True},
    "ha": {"color": [0, 116, 192], "tol": 80, "open_r": 9, "min_area": 600},
    "alg": {"color": [0, 125, 0], "tol": 80, "open_r": 9, "min_area": 600},
}
BARS = {"bars": True, "bar_half": 3, "gap": 30, "bar_w": 8, "margin": 30, "src_px": 8, "x_transform": "pow10"}
LINE = {"color": [217, 80, 20], "tol": 70, "open_r": 4, "max_run": 45, "min_run": 10, "half": 2, "src_px": 8,
        "margin": 30}


def _load(name):
    spec = importlib.util.spec_from_file_location(f"gong2018{name}", Path(__file__).with_name(f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_points(image, key):
    return _load("_points").read_points(image, AXES, {**BARS, **POINTS[key]}, LEGEND)


def read_line(image, at):
    import math
    # `at` are stiffnesses in pN/nm; the axis is log10 of them
    rs = _load("_lines").read_curve(image, [math.log10(a) for a in at], AXES, LINE, LEGEND)
    for r in rs:
        r["x"] = 10.0 ** r["x"]
    return rs
