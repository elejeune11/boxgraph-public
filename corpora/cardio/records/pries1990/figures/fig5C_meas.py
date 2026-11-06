"""Fig. 5, lower panel (network C): number of segments against discharge hematocrit; the filled
circles joined by the solid line (MEASURED). The x axis is calibrated on the ticks above the
top frame line (0.2, 0.4, 0.6, 0.8, labelled below the panel) and the left and right frame lines
(0 and 1); the y axis on the long ticks left of the frame (80, 60, 40, 20) and the bottom frame
line (0). Each point is read at its 0.05 grid position. The circled panel letter is not read."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _pts as P  # noqa: E402

X = dict(edge="top", labels=[0.2, 0.4, 0.6, 0.8], frame_labels={"left": 0.0, "right": 1.0}, pick=P.longest)
Y = dict(edge="left", labels=[80.0, 60.0, 40.0, 20.0], frame_labels={"bottom": 0.0}, pick=P.longest)
EXCLUDE = [(0.88, 1.01, 70.0, 95.0)]  # the circled letter
DIAMETER, OPEN_R = 48, 9
WANT = "filled"
TOL = 0.02


def read(image, at):
    return P.read_points(image, X, Y, DIAMETER, OPEN_R, WANT, exclude=EXCLUDE,
                         at=[float(a) for a in at], at_tol=TOL)
