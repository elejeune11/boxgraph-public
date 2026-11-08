"""Fig. 5D (PDF p. 47): arterial compartment volume, subepicardium (Ep, dashed); x calibrated on the ticks 0, 0.2, 0.4, 0.6 s (0 on the y axis line).

Read by the shared code in _wave.py (see its docstring for the calibration, how the curves are told apart and the intervals).
Tick labels matched: y [1.35, 1.3, 1.25, 1.2, 1.15]; x [0, 0.2, 0.4, 0.6].
"""
import importlib.util
from pathlib import Path

SPEC = {"y": [1.35, 1.3, 1.25, 1.2, 1.15], "x": [0, 0.2, 0.4, 0.6], "x0_on_axis": True, "curve": "dashed", "mask": [[0.865, 0, 0.98, 0.066], [0.82, 0.36, 0.98, 0.447], [0.872, 0.645, 0.98, 0.75]], "max_gap": 80, "grey_gap": 10}


def read(image, at):
    spec = importlib.util.spec_from_file_location("mynard2014_wave", Path(__file__).with_name("_wave.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
