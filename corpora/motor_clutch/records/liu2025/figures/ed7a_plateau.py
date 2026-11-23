"""Extended Data Fig. 7(a) (PDF p. 74): the steady cell traction of the linear KD model's time
courses (master equation, Kelvin-Voigt substrate) for E = 10 kPa, 1 kPa and 100 Pa (top to
bottom, as labelled), read at t = 55 s where the three viscosities' curves lie on top of each
other. Shared code in _hd.py: x ticks 0, 20, 40, 60 s; y ticks 0, 30, 60, 90 Pa. Indexed by E.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_hd", Path(__file__).with_name("_hd.py"))
H = importlib.util.module_from_spec(_s)
_s.loader.exec_module(H)

SPEC = {
    "x": {"marks": [(0, 0), (1, 20), (2, 40), (3, 60)], "major": 0.8},
    "y": {"marks": [(0, 0), (1, 30), (2, 60), (3, 90)], "major": 0.8},
}


def read(image, at):
    return H.plateaus(image, SPEC, 55.0, [1e4, 1e3, 1e2])
