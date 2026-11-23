"""Fig. 9, left panel (PDF p. 8): actin flow against the number of clutches, purple line (the
middle curve).

Read by the shared code in _fig.py (calibration from the printed labels; see its docstring).
The y label "0" sits beside the x label "0" and is left out of the calibration (y_below).
"""
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig.py")

SPEC = {
    "color": (135, 85, 225),
    "others": [(20, 40, 205), (20, 95, 20), (0, 0, 0), (40, 40, 40), (150, 150, 150), (255, 255, 255)],
    "trace": True,
    "tol": 80,
    "gap": 40,
    "y_below": -40,
    "label_sat": 256,
    "x_col_gap": 15,
    "x": {"labels": [0, 1000, 2000, 3000, 4000]},
    "y": {"labels": [60, 50, 40, 30, 20, 10]},
}


def read(image, at):
    spec = importlib.util.spec_from_file_location("panzetta2019_fig", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
