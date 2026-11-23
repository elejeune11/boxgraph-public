"""Extended Data Fig. 6(b) (PDF p. 72): the steady retrograde actin flow of the linear WT model's
time courses (master equation, Kelvin-Voigt substrate) for E = 100 Pa, 1 kPa and 10 kPa (top to
bottom, as labelled), read at t = 55 s where the three viscosities' curves lie on top of each
other. Calibration as ed6a_plateau (loaded from it): x ticks 0, 20, 40, 60 s, y ticks 0, 40, 80,
120 nm/s. Indexed by E.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_ed6a", Path(__file__).with_name("ed6a_plateau.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)
SPEC = B.SPEC


def read(image, at):
    return B.H.plateaus(image, SPEC, 55.0, [1e2, 1e3, 1e4])
