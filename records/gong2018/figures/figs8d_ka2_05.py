"""Fig. S8D (PDF p. 19): spreading speed vs second timescale tau_s2, green open squares
(ka,2 = 0.5).  Read by the shared code in _common.py (see its docstring): axes from the
interior inward ticks; markers by an open-square template.  Markers below tau = 0.25
lie under the other two series and are not read.
"""
import importlib.util
from pathlib import Path

SPEC = {
    "tick_px": 14,
    "x": {"labels": [0.1, 1, 10], "scale": "log10"},
    "y": {"labels": [110, 100, 90, 80]},
    "color": [110, 170, 40], "tol": 70, "square": [19, 11], "score": 0.7, "pad": 40,
    "exclude": [[450, 330, 1120, 670]],
    "src_px": 8,
}


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_common", Path(__file__).with_name("_common.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
