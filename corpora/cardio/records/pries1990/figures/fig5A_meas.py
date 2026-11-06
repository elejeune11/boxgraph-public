"""Fig. 5, upper panel (network A): number of segments against discharge hematocrit; the filled
circles joined by the solid line (MEASURED). The x axis is calibrated on the ticks above the
top frame line (0.2, 0.4, 0.6, 0.8, as labelled under the lower panel, which shares the x axis)
and the left and right frame lines (0 and 1); the y axis on the long ticks left of the frame
(150, 100, 50) and the bottom frame line (0). The points stand on a 0.05 grid; each is read at
its grid position. The legend and the circled panel letter are not read."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _pts as P  # noqa: E402

X = dict(edge="top", labels=[0.2, 0.4, 0.6, 0.8], frame_labels={"left": 0.0, "right": 1.0}, pick=P.longest)
Y = dict(edge="left", labels=[150.0, 100.0, 50.0], frame_labels={"bottom": 0.0}, pick=P.longest)
EXCLUDE = [(0.0, 0.36, 125.0, 170.0), (0.9, 1.01, 125.0, 170.0)]  # the legend; the circled letter
DIAMETER, OPEN_R = 48, 9  # px at 1200 dpi: a marker's diameter; the opening disk (lines are <= 18 px)
WANT = "filled"
TOL = 0.02  # a marker belongs to a grid position within 0.02 (the grid step is 0.05)


def read(image, at):
    out = P.read_points(image, X, Y, DIAMETER, OPEN_R, WANT, exclude=EXCLUDE,
                        at=[float(a) for a in at], at_tol=TOL)
    return out
