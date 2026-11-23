"""Fig. S4 (PDF p. 52): the pink circles, integrin-fibronectin dissociation rates digitized by the
authors from ref. [10] (mean +- s.e.m.), with their error bars.

Calibration as s4_curve (loaded from it): x ticks 0, 15, 30, 45 pN, y log ticks 0.1, 1, 10 s^-1.
Symbols: circle outlines matched to the dark pixels (vector figure), confirmed by the pink fill
inside; error bars: the thin dark vertical line through each symbol's centre, followed up and
down from the outline to the caps.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_s4c", Path(__file__).with_name("s4_curve.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)
SPEC = B.SPEC


def read(image, at):
    return B.H.read_symbols(image, SPEC, (250, 160, 160), 60, "circle", bars=True)
