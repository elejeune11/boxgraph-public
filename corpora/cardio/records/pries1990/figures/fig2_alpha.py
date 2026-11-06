"""Fig. 2: fractional erythrocyte flow FQE against fractional blood flow FQB at one bifurcation;
the filled circles (daughter vessel alpha). Axes: 0 and 1 stand at the frame lines, ticks at
0.25, 0.5 and 0.75 outside the bottom and left frame lines. The legend (upper left) is not read."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _pts as P  # noqa: E402

X = dict(edge="bottom", labels=[0.25, 0.5, 0.75], frame_labels={"left": 0.0, "right": 1.0}, pick=P.longest)
Y = dict(edge="left", labels=[0.75, 0.5, 0.25], frame_labels={"top": 1.0, "bottom": 0.0}, pick=P.longest)
LEGEND = (0.0, 0.5, 0.86, 1.01)
DIAMETER, OPEN_R = 34, 7  # px at 800 dpi: a marker's diameter; the opening disk (lines are <= 12 px)
WANT = "filled"


def read(image, at):
    return P.read_points(image, X, Y, DIAMETER, OPEN_R, WANT, exclude=LEGEND)
