"""Fig. 9, right panel (PDF p. 8): actin flow against the substrate spring constant, green
line (the highest curve, at the head of the arrow labelled x0).

Read by the shared code in _fig.py (calibration from the printed labels; see its docstring).
The y label "0" sits beside the x label "0" and is left out of the calibration (y_below).
"""
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig.py")

SPEC = {
    "color": (20, 95, 20),
    "others": [(20, 40, 205), (135, 85, 225), (0, 0, 0), (40, 40, 40), (150, 150, 150), (255, 255, 255)],
    "trace": True,
    "tol": 80,
    "gap": 80,
    "y_below": -40,
    "label_sat": 256,
    "x_col_gap": 15,
    "x": {"labels": [0, 50, 100, 150, 200]},
    "y": {"labels": [120, 100, 80, 60, 40, 20]},
}


def read(image, at):
    spec = importlib.util.spec_from_file_location("panzetta2019_fig", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
