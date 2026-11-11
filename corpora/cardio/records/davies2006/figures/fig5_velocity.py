"""Fig. 5, lower panel (PDF p. 7): coronary flow velocity (dashed line, left axis), LVH subject's
circumflex artery.

Read by the shared code in _traces.py (dashes followed from dash to dash; the panel title blanked).
Tick labels matched: left y axis 0.4, 0.3, 0.2, 0.1, 0 m/s (top to bottom); x 0, 100, ..., 900 ms.
"""
import importlib.util
from pathlib import Path

SPEC = {"panel": 2, "axis": "left", "kind": "dashed", "start": "upper", "y": [0.4, 0.3, 0.2, 0.1, 0],
        "x": [0, 100, 200, 300, 400, 500, 600, 700, 800, 900],
        "mask": [[0.0, 0.0, 0.51, 0.075]]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("davies2006_traces", Path(__file__).with_name("_traces.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_pu(image, at, SPEC)
