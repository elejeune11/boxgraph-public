"""Fig. 9E (PDF p. 51): the solid grey line: double Cpa; x: no ticks on this axis; read as the fraction of the plotted interval, 0 at the y axis line and 1 at the right end of the x axis line.

Read by the shared code in _wave.py (see its docstring for the calibration, how the curves are told apart and the intervals).
Tick labels matched: y [80, 60, 40, 20, 0, -20].
"""
import importlib.util
from pathlib import Path

SPEC = {"y": [80, 60, 40, 20, 0, -20], "curve": "grey", "mask": [[0, 0, 0.1, 0.12], [0.686, 0.044, 0.962, 0.148], [0.682, 0.148, 0.724, 0.24], [0.578, 0.84, 1.0, 0.95]]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("mynard2014_wave", Path(__file__).with_name("_wave.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
