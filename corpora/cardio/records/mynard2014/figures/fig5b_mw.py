"""Fig. 5B (PDF p. 47): arterial side, midwall (MW, solid grey); x calibrated on the ticks 0, 0.2, 0.4, 0.6 s (0 on the y axis line).

Read by the shared code in _wave.py (see its docstring for the calibration, how the curves are told apart and the intervals).
Tick labels matched: y [1, 0.5, 0, -0.5]; x [0, 0.2, 0.4, 0.6].
"""
import importlib.util
from pathlib import Path

SPEC = {"y": [1, 0.5, 0, -0.5], "x": [0, 0.2, 0.4, 0.6], "x0_on_axis": True, "curve": "grey", "mask": [[0.6, 0, 0.71, 0.055], [0.64, 0.19, 0.805, 0.272], [0.778, 0.47, 0.892, 0.57]], "max_gap": 80, "grey_gap": 10}


def read(image, at):
    spec = importlib.util.spec_from_file_location("mynard2014_wave", Path(__file__).with_name("_wave.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
