"""Fig. 3, middle panel (PDF p. 5): the troughs of WI- (local minima of the traced line with a
prominence above 0.1 x 10^5 W m^-2 s^-2), each at the time it occurs.

Read by the shared code in _traces.py, as fig3_wi_minus.
"""
import importlib.util
from pathlib import Path

SPEC = {"panel": 1, "kind": "lower", "y": [0, -0.5, -1, -1.5, -2], "mult": 1e5, "peaks": 0.1,
        "x": [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("davies2006_traces", Path(__file__).with_name("_traces.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_wi(image, at, SPEC)
