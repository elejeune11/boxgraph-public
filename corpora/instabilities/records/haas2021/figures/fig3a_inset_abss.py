"""Fig. 3(a), inset (PDF p. 10): alphabar_ss unscaled, the dark blue U-shaped curve.

Reading by the shared code in _fig3.py (see its docstring for the calibration, the curve mask and
the intervals). Curve colour (0, 0, 204), sampled from the rendered page; legend samples are dropped as
parts narrower than 500 columns. Tick labels matched: x [-1, -0.5, 0.5, 1]; y ticks [20, 40] (the inset has no minor ticks).
"""
import importlib.util
from pathlib import Path

SPEC = {"color": (0, 0, 204), "x_labels": [-1, -0.5, 0.5, 1], "y_ticks": [20, 40], "min_width": 300}


def read(image, at):
    spec = importlib.util.spec_from_file_location("haas2021_fig3", Path(__file__).with_name("_fig3.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
