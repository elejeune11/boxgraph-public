"""Fig. 1G (p. 2): bulk tissue concentration <C_tissue>/C_inlet against the number of vessels (log axis),
moving averages of lattice (blue in i, green in ii) and synthetic vasculature (orange in i, red in ii).
Panel i is the convex cube domain, panel ii the nonconvex biventricle.

Calibration: the plot's y axis is the long vertical line to the right of the colour bar (the rightmost
long vertical line; the colour bar's edges lie left of it); its tick labels (1.0 ... 0.0) are printed
left of the colour bar in both panels; y ticks out to the left, labels 1.0 ... 0.0. The x
axis is a log axis with labelled decade ticks 10^1, 10^2, 10^3 (the long ticks below the axis: runs of at
least 22 px at 1000 dpi; minor ticks are about 16 px). See _curves.py for the tracing.

Seeds: each curve is traced from x = 100 (10^2), where no inset image or its outline lies on it in either
panel; there the lattice curve is the lower run and the vasculature curve the upper run of its colour,
except in panel i where the two have different colours.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _curves as K  # noqa: E402

COLOURS = {"lat_i": (31, 110, 175), "vas_i": (235, 125, 30), "lat_ii": (60, 150, 60), "vas_ii": (205, 40, 40)}


def read(image, at, which):
    ax_x, ax_y, box = K.axes(image, [1.0, 0.8, 0.6, 0.4, 0.2, 0.0], [10, 100, 1000], xscale="log10", yrank=-1,
                             xlen=25, xmin=22)
    return K.read_traced(image, at, ax_x, ax_y, box, COLOURS[which], 70, 100, pick="lowest")
