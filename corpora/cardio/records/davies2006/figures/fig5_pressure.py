"""Fig. 5, lower panel (PDF p. 7): coronary blood pressure (solid line, right axis), LVH subject's
circumflex artery.

Read by the shared code in _traces.py (solid line traced; the panel title, which stands inside the
panel's top, blanked). Tick labels matched: right y axis 120, 110, 100, 90, 80, 70 mmHg (top to
bottom); x 0, 100, ..., 900 ms.
"""
import importlib.util
from pathlib import Path

SPEC = {"panel": 2, "axis": "right", "kind": "solid", "start": "lower", "y": [120, 110, 100, 90, 80, 70],
        "x": [0, 100, 200, 300, 400, 500, 600, 700, 800, 900],
        "mask": [[0.0, 0.0, 0.51, 0.075]]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("davies2006_traces", Path(__file__).with_name("_traces.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_pu(image, at, SPEC)
