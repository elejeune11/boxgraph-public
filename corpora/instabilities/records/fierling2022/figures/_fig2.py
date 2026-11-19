"""Shared calibration for the angular-profile panels Fig. 2c and Supp. Fig. 1f (gnuplot, see _gp.py).

x: the left frame line carries the printed 0 and the right frame line pi/2; the two long inward
ticks (major ticks; the short ones every pi/24 are minor) carry the printed pi/8 and pi/4, left to
right. The bottom frame's ticks are partly hidden by lines lying on zero, so the mirrored ticks on
the top frame line are used when the bottom ones are not all seen.
y: the frame lines and the major inward ticks on the left frame line, matched top to bottom to the
printed labels given by each panel.
"""
import math

import _gp

XLABELS = [(0.0, "frame-left"), (math.pi / 8, "tick:0"), (math.pi / 4, "tick:1"), (math.pi / 2, "frame-right")]


def read_line(image, at, ylabels, rgb, rows):
    spec = {"ylabels": ylabels, "xlabels": XLABELS, "rgb": rgb, "tol": 40, "win": 25, "rows": rows}
    return _gp.read_lines(image, at, spec)
