"""Fig. 3 D, bottom row (PDF p. 4): the local F-actin speed of a single FA against time, one black dot per frame.

Matched labels: y 0, 5, 10 (step 5; 0 at the bottom edge); x 0, 2, ..., 14 (the bottom row's labels; 0 at the left edge).
See _series.py.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("gardel_series", Path(__file__).with_name("_series.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


def read(image, at):
    return S.read_strip(image, 5)
