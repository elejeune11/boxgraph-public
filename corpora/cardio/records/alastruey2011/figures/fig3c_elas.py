"""Fig. 3c (PDF p. 6): Left renal pressure at the midpoint, the thin solid line (elas, purely elastic 1-D simulation).

Reading by the shared code in _fig3.py (see its docstring for the calibration, how the three
curves are told apart and the intervals). Tick labels matched: x [0.2, 0.4, 0.6, 0.8] s; y [16, 14, 12, 10] kPa.
"""
import importlib.util
from pathlib import Path

SPEC = {"curve": "elas", "x": [0.2, 0.4, 0.6, 0.8], "y": [16, 14, 12, 10]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("alastruey2011_fig3", Path(__file__).with_name("_fig3.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
