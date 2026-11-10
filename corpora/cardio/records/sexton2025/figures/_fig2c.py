"""Fig. 2C (p. 3): alignment with the brute-force finite-difference optimum against bifurcation depth B;
solid lines are the median alignment (red: approximation, blue: partial binding; shading min-max, N = 100).

Calibration: y axis (left frame line), ticks out to the left, labels 1.0 ... 0.0 (major ticks are
longer than the minor ones: runs of at least 30 px at 1000 dpi); x axis (bottom frame line), major ticks
below it labelled 10 ... 80 (the 0 label's tick is the y axis). The lines are told from their lighter
min-max shading by colour (within 70 of the line colour). Seeds at B = 40, where each line is the only
run of its colour. See _curves.py.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _curves as K  # noqa: E402

COLOURS = {"approx": (230, 35, 45), "pb": (45, 80, 165)}


def read(image, at, which):
    ax_x, ax_y, box = K.axes(image, [1.0, 0.8, 0.6, 0.4, 0.2, 0.0], [10, 20, 30, 40, 50, 60, 70, 80],
                             ylen=40, ymin=30, xlen=40, xmin=30)
    return K.read_traced(image, at, ax_x, ax_y, box, COLOURS[which], 70, 40, pick="lowest")
