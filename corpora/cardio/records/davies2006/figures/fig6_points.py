"""Fig. 6 (PDF p. 8): backward-traveling suction wave % against LV septum (cm), one marker per subject.

Read by the shared code in _scatter.py (calibration from the grey ticks, markers as black blobs
opened free of the regression line and the r/p text, fused markers split).
Tick labels matched: y 0, 5, ..., 45 (bottom to top); x 0, 0.5, 1, 1.5, 2.
"""
import importlib.util
from pathlib import Path

Y = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45]
X = [0, 0.5, 1, 1.5, 2]


def read(image, at):
    spec = importlib.util.spec_from_file_location("davies2006_scatter", Path(__file__).with_name("_scatter.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_points(image, Y, X)
