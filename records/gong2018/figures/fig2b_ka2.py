"""Fig. 2B (PDF p. 4): mean spreading speed vs viscosity, kl = 0.1 pN/nm, green open
squares (ka = 2).  Read by the shared code in _common.py (see its docstring): axes from
the interior inward ticks (0.1, 1, 10; 110 to 70: the end ticks sit in the spines);
markers by an open-square template.  The marker at the left spine is not read.
"""
import importlib.util
from pathlib import Path

SPEC = {
    "x": {"labels": [0.1, 1, 10], "scale": "log10"},
    "y": {"labels": [110, 100, 90, 80, 70]},
    "color": [10, 125, 10], "tol": 80, "square": [28, 19], "score": 0.7, "pad": 40,
    "src_px": 8,
}


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_common", Path(__file__).with_name("_common.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
