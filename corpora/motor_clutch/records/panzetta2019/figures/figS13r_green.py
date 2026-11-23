"""Fig. S13, right panel (PDF p. 23): the modified (two-spring) model, green series (diamond
markers; the largest x0 of the three, per the legend).

Read by the shared code in _fig.py (calibration from the printed labels; see its docstring).
"""
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig.py")

SPEC = {
    "color": (10, 105, 35),
    "others": [(10, 10, 205), (110, 10, 205), (0, 0, 0), (255, 255, 255)],
    "tol": 80,
    "gap": 120,
    "min_area": 150,
    "x": {"labels": [0.1, 1, 10, 100], "scale": "log10"},
    "y": {"labels": [22, 20, 18, 16, 14, 12, 10, 8, 6]},
}


def read(image, at):
    spec = importlib.util.spec_from_file_location("panzetta2019_fig", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
