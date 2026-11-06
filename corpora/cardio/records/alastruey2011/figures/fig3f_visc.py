"""Fig. 3f (PDF p. 6): Right iliac-femoral III flow rate at the midpoint, the thick dashed line (visc, visco-elastic 1-D simulation).

Reading by the shared code in _fig3.py (see its docstring for the calibration, how the three
curves are told apart and the intervals). Tick labels matched: x [0.2, 0.4, 0.6, 0.8] s; y [10, 5] mL/s.
"""
import importlib.util
from pathlib import Path

SPEC = {"curve": "visc", "x": [0.2, 0.4, 0.6, 0.8], "y": [10, 5]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("alastruey2011_fig3", Path(__file__).with_name("_fig3.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
