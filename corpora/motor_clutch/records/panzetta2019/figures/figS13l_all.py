"""Fig. S13, left panel (PDF p. 23): the canonical clutch model, all three series together.

The blue, purple and green markers (three values of x0, per the legend) lie on one curve, so
the reading takes the pixels of all three colours as one series. Read by the shared code in
_fig.py (calibration from the printed labels; see its docstring for the method and intervals).
"""
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig.py")

SPEC = {
    "colors": [(36, 108, 252), (108, 12, 204), (12, 108, 36)],
    "others": [(0, 0, 0), (255, 255, 255)],
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
