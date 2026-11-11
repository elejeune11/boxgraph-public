"""Fig. 5, upper panel (PDF p. 7): WI+ (waves originating proximally), circumflex artery of the LVH
subject (septal wall thickness 1.6 cm).

Read by the shared code in _traces.py: the top edge of the trace, on the time axis of the bottom
panel. Tick labels matched: y 6, 5, 4, 3, 2, 1, 0 (x 10^5, top to bottom); x 0, 100, ..., 900 ms.
"""
import importlib.util
from pathlib import Path

SPEC = {"panel": 0, "kind": "upper", "y": [6, 5, 4, 3, 2, 1, 0], "mult": 1e5,
        "x": [0, 100, 200, 300, 400, 500, 600, 700, 800, 900]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("davies2006_traces", Path(__file__).with_name("_traces.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_wi(image, at, SPEC)
