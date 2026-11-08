"""Fig. 9F (PDF p. 51): the dashed black line: half V0; x: no ticks on this axis; read as the fraction of the plotted interval, 0 at the y axis line and 1 at the right end of the x axis line.

Read by the shared code in _wave.py (see its docstring for the calibration, how the curves are told apart and the intervals).
Tick labels matched: y [80, 60, 40, 20, 0, -20].
"""
import importlib.util
from pathlib import Path

SPEC = {"y": [80, 60, 40, 20, 0, -20], "curve": "dashed", "mask": [[0, 0, 0.1, 0.12], [0.676, 0.087, 1.0, 0.181], [0.848, 0.181, 0.876, 0.312], [0.718, 0.596, 0.97, 0.69], [0.752, 0.515, 0.785, 0.6]]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("mynard2014_wave", Path(__file__).with_name("_wave.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
