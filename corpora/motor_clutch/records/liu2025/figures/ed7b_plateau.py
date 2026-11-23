"""Extended Data Fig. 7(b) (PDF p. 74): the steady retrograde actin flow of the linear KD model's
time courses for E = 100 Pa, 1 kPa and 10 kPa (top to bottom, as labelled), read at t = 55 s.
Shared code in _hd.py: x ticks 0, 20, 40, 60 s; y ticks 0, 40, 80, 120 nm/s. Indexed by E.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_hd", Path(__file__).with_name("_hd.py"))
H = importlib.util.module_from_spec(_s)
_s.loader.exec_module(H)

SPEC = {
    "x": {"marks": [(0, 0), (1, 20), (2, 40), (3, 60)], "major": 0.8},
    "y": {"marks": [(0, 0), (1, 40), (2, 80), (3, 120)], "major": 0.8},
}


def read(image, at):
    return H.plateaus(image, SPEC, 55.0, [1e2, 1e3, 1e4])
