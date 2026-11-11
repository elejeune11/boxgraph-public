"""Fig. 7 (PDF p. 8): forward-traveling suction wave % against "Age (years)", one marker per subject.

Read by the shared code in _scatter.py (calibration from the grey ticks, markers as black blobs
opened free of the regression line and the r/p text, fused markers split).
Tick labels matched: y 0, 10, ..., 80 (bottom to top); x 0, 10, 20, 30, as printed on the axis
(which disagrees with the cohort's ages, q_fig7_axes).
"""
import importlib.util
from pathlib import Path

Y = [0, 10, 20, 30, 40, 50, 60, 70, 80]
X = [0, 10, 20, 30]


def read(image, at):
    spec = importlib.util.spec_from_file_location("davies2006_scatter", Path(__file__).with_name("_scatter.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_points(image, Y, X)
