"""Fig. 5A (PDF p. 47): total microvascular arterial flow (solid, 'arterial'); x calibrated on the ticks 0, 0.2, 0.4, 0.6 s (0 on the y axis line).

Read by the shared code in _wave.py (see its docstring for the calibration, how the curves are told apart and the intervals).
Tick labels matched: y [3, 2, 1, 0]; x [0, 0.2, 0.4, 0.6].
"""
import importlib.util
from pathlib import Path

SPEC = {"y": [3, 2, 1, 0], "x": [0, 0.2, 0.4, 0.6], "x0_on_axis": True, "curve": "solid", "mask": [[0.2, 0, 0.5, 0.05], [0.77, 0, 1.0, 0.105], [0.277, 0.85, 0.905, 0.95], [0.563, 0.762, 0.585, 0.97]], "max_gap": 80, "grey_gap": 10}


def read(image, at):
    spec = importlib.util.spec_from_file_location("mynard2014_wave", Path(__file__).with_name("_wave.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
