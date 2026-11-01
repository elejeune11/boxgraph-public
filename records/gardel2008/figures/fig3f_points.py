"""Fig. 3 F (PDF p. 4): F-actin speed at ts, v(ts), against traction stress at ts, sigma(ts),
one black dot per FA.

Matched labels: x 40, 60, 80, 100, 120 under the long ticks (40 under the leftmost); the short
ticks lie halfway. The left frame edge carries a "0" label but does not lie on the tick grid
(it falls about 22 Pa on it, and no "20" label is printed), so the x axis is calibrated on the
ticks alone and the "0" label is not used. y: 0, 5, ..., 30 (0 at the bottom edge, 30 at the
top), short ticks halfway. See _dots.py for the markers.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("gardel_dots", Path(__file__).with_name("_dots.py"))
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)


def read(image, at):
    mask = D.L.neutral_dark(image, 110)
    return D.read_markers(image, mask, (0.0, 120.0), 20.0, (0.0, 30.0), 5.0, what="black dot",
                          x_first_major=40.0)
