"""Fig. 5, middle panel (PDF p. 7): the troughs of WI- (local minima of the traced line with a
prominence above 0.1 x 10^5 W m^-2 s^-2), each at its time; LVH subject.

Read by the shared code in _traces.py, as fig5_wi_minus.
"""
import importlib.util
from pathlib import Path

SPEC = {"panel": 1, "kind": "lower", "y": [0, -1, -2], "mult": 1e5, "peaks": 0.1,
        "x": [0, 100, 200, 300, 400, 500, 600, 700, 800, 900],
        # the circled labels 1 and 5 touch the tips of their troughs: blanked below the tips
        "mask": [[0.142, 0.288, 0.184, 0.56], [0.477, 0.873, 0.519, 1.0]]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("davies2006_traces", Path(__file__).with_name("_traces.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_wi(image, at, SPEC)
