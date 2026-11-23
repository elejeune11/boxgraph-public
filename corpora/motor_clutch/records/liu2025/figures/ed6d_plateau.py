"""Extended Data Fig. 6(d) (PDF p. 72): the steady large-scale substrate deformation xs of the
linear WT model (master equation, Kelvin-Voigt substrate) for E = 100 Pa, 1 kPa and 10 kPa (top
to bottom, as labelled), read at t = 55 s on the red (xi_s = 0) and green (xi_s = 1 pN s/nm)
curves, which have reached their plateaus and lie on top of each other there. The blue curves
(xi_s = 10^3 pN s/nm) are still rising and are not read.

Shared code in _hd.py. x: ticks 0, 20, 40, 60 s; y: ticks 0, 50, 100, 150 nm. Indexed by E.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_hd", Path(__file__).with_name("_hd.py"))
H = importlib.util.module_from_spec(_s)
_s.loader.exec_module(H)

SPEC = {
    "x": {"marks": [(0, 0), (1, 20), (2, 40), (3, 60)], "major": 0.8},
    "y": {"marks": [(0, 0), (1, 50), (2, 100), (3, 150)], "major": 0.8},
}
RED_GREEN = [((230, 30, 30), 110), ((40, 220, 40), 110)]


def read(image, at):
    return H.plateaus(image, SPEC, 55.0, [1e2, 1e3, 1e4], colours=RED_GREEN)
