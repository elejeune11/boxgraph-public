"""Fig. 3, middle panel (PDF p. 5): WI- (waves originating distally), one subject's circumflex artery.

Read by the shared code in _traces.py: the bottom edge of the trace (acceleration waves are filled
above it), on the time axis of the bottom panel. Tick labels matched: y 0, -0.5, -1, -1.5, -2
(x 10^5, top to bottom); x 0, 100, ..., 1000 ms.
"""
import importlib.util
from pathlib import Path

SPEC = {"panel": 1, "kind": "lower", "y": [0, -0.5, -1, -1.5, -2], "mult": 1e5,
        "x": [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("davies2006_traces", Path(__file__).with_name("_traces.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_wi(image, at, SPEC)
