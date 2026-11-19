"""Shared calibration for Fig. 3a (PDF p. 7), apical area fold change against time (gnuplot, see _gp.py).

y (left axis, area): the frame lines carry the printed 1.2 (top) and 0 (bottom); the major inward
ticks on the left frame line between them are matched to 1, 0.8, 0.6, 0.4, 0.2.
x: the left and right frame lines carry the printed -7 and 4 (the plotted range; the first and
last labels shown are -6 and 4); the inward ticks on the bottom frame line carry -6, -4, -2, 0, 2.
A line is the run of its colour near each position (see _gp.read_lines). The MyoII curves use the
right axis and other colours (dotted slate, dotted red) and are not read here.
"""
import _gp

YLABELS = [1.2, 1.0, 0.8, 0.6, 0.4, 0.2, 0.0]
XLABELS = [(-7.0, "frame-left"), (-6.0, "tick:0"), (-4.0, "tick:1"), (-2.0, "tick:2"), (0.0, "tick:3"),
           (2.0, "tick:4"), (4.0, "frame-right")]


def read(image, at, rgb, rows):
    return _gp.read_lines(image, at, {"ylabels": YLABELS, "xlabels": XLABELS, "rgb": rgb, "tol": 40,
                                      "win": 12, "rows": rows})
