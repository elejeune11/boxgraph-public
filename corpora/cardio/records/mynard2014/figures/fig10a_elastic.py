"""Fig. 10A (PDF p. 52): the solid line (purely elastic wall law); x calibrated on the ticks 11.1, 11.2, 11.3 mm^2.

Read by the shared code in _wave.py (see its docstring for the calibration, how the curves are told apart and the intervals).
Tick labels matched: y [75, 70, 65, 60]; x [11.1, 11.2, 11.3].
"""
import importlib.util
from pathlib import Path

SPEC = {"y": [75, 70, 65, 60], "x": [11.1, 11.2, 11.3], "curve": "solid", "mask": [[0, 0, 0.12, 0.1]]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("mynard2014_wave", Path(__file__).with_name("_wave.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
