"""Fig. 5C (PDF p. 47): venous side, subepicardium (Ep, dashed); x calibrated on the ticks 0, 0.2, 0.4, 0.6 s (0 on the y axis line).

Read by the shared code in _wave.py (see its docstring for the calibration, how the curves are told apart and the intervals).
Tick labels matched: y [1, 0.8, 0.6, 0.4, 0.2, 0]; x [0, 0.2, 0.4, 0.6].
"""
import importlib.util
from pathlib import Path

SPEC = {"y": [1, 0.8, 0.6, 0.4, 0.2, 0], "x": [0, 0.2, 0.4, 0.6], "x0_on_axis": True, "curve": "dashed", "mask": [[0.24, 0, 0.35, 0.065], [0.153, 0.262, 0.312, 0.345], [0.159, 0.468, 0.266, 0.57]], "max_gap": 80, "grey_gap": 10}


def read(image, at):
    spec = importlib.util.spec_from_file_location("mynard2014_wave", Path(__file__).with_name("_wave.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
