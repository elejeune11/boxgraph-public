"""Fig. S8D (PDF p. 19): spreading speed vs second timescale tau_s2, blue open circles
(ka,2 = 1).  Read by the shared code in _common.py (see its docstring): axes from the
interior inward ticks; markers by an annulus template.  Markers below tau = 0.1 lie
under the orange triangles and are not read.
"""
import importlib.util
from pathlib import Path

SPEC = {
    "tick_px": 14,
    "x": {"labels": [0.1, 1, 10], "scale": "log10"},
    "y": {"labels": [110, 100, 90, 80]},
    "color": [10, 110, 190], "tol": 80, "ring": [17, 27], "score": 0.6, "pad": 40,
    "exclude": [[450, 330, 1120, 670]],
    "src_px": 8,
}


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_common", Path(__file__).with_name("_common.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
