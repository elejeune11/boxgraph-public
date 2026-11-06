"""Fig. 6: average flow velocity of arteriovenous segments against generation; the filled circles
on the solid line (MEASURED, ref. 17). The x axis is calibrated on the ticks below the bottom
frame line (5, 10, 15, 20) and the left and right frame lines (0 and 25); the y axis on the ticks
left of the frame (2, 1.5, 1, 0.5) and the bottom frame line (0). Every filled marker is read at
the generation read from the image. The legend (upper right) is not read."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _pts as P  # noqa: E402

X = dict(edge="bottom", labels=[5.0, 10.0, 15.0, 20.0], frame_labels={"left": 0.0, "right": 25.0}, pick=P.longest)
Y = dict(edge="left", labels=[2.0, 1.5, 1.0, 0.5], frame_labels={"bottom": 0.0}, pick=P.longest)
EXCLUDE = [(14.5, 25.5, 1.7, 2.3)]  # the legend
DIAMETER, OPEN_R = 40, 8  # px at 1000 dpi
WANT = "filled"


def read(image, at):
    return P.read_points(image, X, Y, DIAMETER, OPEN_R, WANT, exclude=EXCLUDE)
