"""Fig. 7(a) (PDF p. 10), path via the head: peak backward wave intensity (red circles).

Reading by the shared code in _fig7.py (see its docstring). Tick labels matched:
x [20, 40, 60, 80, 100] cm; y [7, 6, 5, 4, 3, 2, 1, 0] (log10 W/m^2/s^2).
"""
import importlib.util
from pathlib import Path

SPEC = {"curve": "backward", "x": [20, 40, 60, 80, 100], "y": [7, 6, 5, 4, 3, 2, 1, 0]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("mynard2015_fig7", Path(__file__).with_name("_fig7.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
