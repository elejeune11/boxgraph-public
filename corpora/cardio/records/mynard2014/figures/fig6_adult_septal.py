"""Fig. 6 (upper row, septal (segment 17)) (PDF p. 48): simulated mean normalised flow, representative adult model, septal (segment 17); y calibrated on the row's shared y axis; x: no ticks; read as the fraction of the panel between its two vertical box lines.

Read by the shared code in _wave.py (see its docstring for the calibration, how the curves are told apart and the intervals).
Tick labels matched: y [4, 3, 2, 1, 0, -1].
"""
import importlib.util
from pathlib import Path

SPEC = {"y": [4, 3, 2, 1, 0, -1], "subpanel": 2, "curve": "solid"}


def read(image, at):
    spec = importlib.util.spec_from_file_location("mynard2014_wave", Path(__file__).with_name("_wave.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
