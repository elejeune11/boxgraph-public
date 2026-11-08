"""Fig. 3 (CEP) (PDF p. 45): CEP, subendocardial layer (solid line, 'Subendo.'); x: unlabelled ticks, read as 0.2 s apart from the scale label '0.2 s' under the first interval of the LVE panel, 0 on the y axis line (the fit to the four positions checks the spacing).

Read by the shared code in _wave.py (see its docstring for the calibration, how the curves are told apart and the intervals).
Tick labels matched: y [100, 50]; x [0, 0.2, 0.4, 0.6].
"""
import importlib.util
from pathlib import Path

SPEC = {"y": [100, 50], "x": [0, 0.2, 0.4, 0.6], "x0_on_axis": True, "curve": "solid", "mask": [[0.62, 0, 1.0, 0.13], [0.62, 0.17, 1.0, 0.31], [0.65, 0.4, 1.0, 0.55], [0.65, 0.62, 1.0, 0.76]]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("mynard2014_wave", Path(__file__).with_name("_wave.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
