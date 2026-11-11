"""Fig. 3, upper panel (PDF p. 5): WI+ (waves originating proximally), one subject's circumflex artery.

Read by the shared code in _traces.py: the top edge of the trace (acceleration waves are filled
below it), on the time axis of the bottom panel. Tick labels matched: y 2, 1.5, 1, 0.5, 0 (x 10^5,
top to bottom); x 0, 100, ..., 1000 ms.
"""
import importlib.util
from pathlib import Path

SPEC = {"panel": 0, "kind": "upper", "y": [2, 1.5, 1, 0.5, 0], "mult": 1e5,
        "x": [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("davies2006_traces", Path(__file__).with_name("_traces.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_wi(image, at, SPEC)
