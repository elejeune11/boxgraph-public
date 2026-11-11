"""Fig. 3, lower panel (PDF p. 5): coronary blood pressure (solid line, right axis), one subject's
circumflex artery.

Read by the shared code in _traces.py (solid line traced; the curve labels blanked). Tick labels
matched: right y axis 140, 120, 100, 80 mmHg (top to bottom); x 0, 100, ..., 1000 ms.
"""
import importlib.util
from pathlib import Path

SPEC = {"panel": 2, "axis": "right", "kind": "solid", "start": "lower", "y": [140, 120, 100, 80],
        "x": [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
        "mask": [[0.6346, 0.09, 0.704, 0.183], [0.645, 0.183, 0.704, 0.2], [0.6907, 0.183, 0.704, 0.22], [0.563, 0.655, 0.643, 0.77]]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("davies2006_traces", Path(__file__).with_name("_traces.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_pu(image, at, SPEC)
