"""Fig. 7B (PDF p. 49): simulated proximal Cx flow (dashed line), adult sheep panel B; x: no ticks on this axis; read as the fraction of the plotted interval, 0 at the y axis line and 1 at the right end of the x axis line.

Read by the shared code in _wave.py (see its docstring for the calibration, how the curves are told apart and the intervals).
Tick labels matched: y [150, 100, 50, 0, -50].
"""
import importlib.util
from pathlib import Path

SPEC = {"y": [150, 100, 50, 0, -50], "curve": "dashed", "open": 21, "mask": [[0, 0, 0.12, 0.2], [0.11, 0.0, 0.19, 0.44], [0.535, 0.0, 0.605, 0.25]]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("mynard2014_wave", Path(__file__).with_name("_wave.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
