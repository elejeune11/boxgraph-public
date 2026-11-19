"""Fig. 2a (PDF p. 5): the dotted steel-blue step line 'Target size, AP and DV' (midline pre-strain 0.43).

Calibration in _fig2a.py: top frame 1.05, the reference line 1, inward ticks 0.95, 0.9, 0.85, 0.8, 0.75,
bottom frame 0.7. In the first angular bands the line lies on the bottom frame line: it is read
from its upper edge plus its half thickness measured where it is clear.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig2a  # noqa: E402

Y = [(1.05, "frame-top"), (1.0, "hline"), (0.95, "tick:0"), (0.9, "tick:1"), (0.85, "tick:2"),
     (0.8, "tick:3"), (0.75, "tick:4"), (0.7, "frame-bottom")]


def read(image, at):
    return _fig2a.read_line(image, at, Y, _fig2a.STEELBLUE, (0.68, 1.02))
