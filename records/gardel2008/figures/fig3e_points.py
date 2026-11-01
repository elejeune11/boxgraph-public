"""Fig. 3 E (PDF p. 4): F-actin speed at ts, v(ts), against adhesion age ts, one black dot per FA.

Matched labels: x 0, 2, 4, 6, 8 on the long ticks (0 at the left frame edge), short ticks
halfway; y 0, 5, ..., 30 (0 at the bottom frame edge, 30 at the top), short ticks halfway.
See _dots.py for how markers are found and separated.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("gardel_dots", Path(__file__).with_name("_dots.py"))
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)


def read(image, at):
    mask = D.L.neutral_dark(image, 110)
    return D.read_markers(image, mask, (0.0, 9.0), 2.0, (0.0, 30.0), 5.0, what="black dot")
