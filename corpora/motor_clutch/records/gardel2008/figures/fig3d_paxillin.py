"""Fig. 3 D, third row (PDF p. 4): the GFP-paxillin intensity (axis in 10^4 arbitrary units) of a single FA against time, one black dot per frame.

Matched labels: y 0, 3, 6 (step 3; 0 at the bottom edge); x 0, 2, ..., 14 (the bottom row's labels; 0 at the left edge).
See _series.py.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("gardel_series", Path(__file__).with_name("_series.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


def read(image, at):
    return S.read_strip(image, 3)
