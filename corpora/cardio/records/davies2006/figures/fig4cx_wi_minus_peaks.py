"""Fig. 4, upper panel (PDF p. 6): circumflex artery of one subject; the troughs of WI- (local minima of the traced bottom edge, prominence above 0.1 x 10^5 W m^-2 s^-2).

Read by the shared code in _traces.py (see its note on Fig. 4: a blurred scan with boxed
panels; ticks searched 3-20 px inside the frame). Tick labels matched top to bottom on the
y axis and left to right on x (0 to 1000 ms), as in SPEC.
"""
import importlib.util
from pathlib import Path

SPEC = {"panel": 0, "kind": "lower", "y": [2, 1.5, 1, 0.5, 0, -0.5, -1, -1.5, -2], "mult": 1e5, "peaks": 0.1, "x": [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000], "ytick": (3, 20), "xtick": (3, 20)}

def read(image, at):
    spec = importlib.util.spec_from_file_location("davies2006_traces", Path(__file__).with_name("_traces.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_wi(image, at, SPEC)
