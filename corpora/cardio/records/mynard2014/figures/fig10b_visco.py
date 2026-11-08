"""Fig. 10B (PDF p. 52): simulated Cx flow, the dashed line (viscoelastic wall law); x calibrated on the ticks 0, 0.2, 0.4 s (0 on the y axis line).

Read by the shared code in _wave.py (see its docstring for the calibration, how the curves are told apart and the intervals).
Tick labels matched: y [80, 60, 40, 20, 0, -20]; x [0, 0.2, 0.4].
"""
import importlib.util
from pathlib import Path

SPEC = {"y": [80, 60, 40, 20, 0, -20], "x": [0, 0.2, 0.4], "x0_on_axis": True, "curve": "dashed", "mask": [[0, 0, 0.1, 0.1]]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("mynard2014_wave", Path(__file__).with_name("_wave.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
