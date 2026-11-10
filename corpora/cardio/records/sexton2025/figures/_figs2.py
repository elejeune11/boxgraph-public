"""Fig. S2D-F (p. 39): times (s) against tree size for array and linked-list containers; lines are means,
shading +-2 SD over 100 reruns (caption). The y labels are printed with a common factor at the top of
the axis (x10^-2 in D, x10^-4 in E, x10^-3 in F); the labels passed below include it.

Calibration: frame lines (dark < 160); y ticks out to the left (6 in D: 0.0 ... 5.0; 9 in E: 0.0 ... 8.0;
5 in F: 0.0 ... 4.0), x ticks out below, labelled 200, 400, 600, 800. Lines are told from their lighter
shading by colour (within 50 of the line colour, the plotting library's standard blue, orange, green and
red). Each line is traced from the seed x given below, where it is the run of its colour nearest the
given height (a fraction of the plot from its top). See _curves.py.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _curves as K  # noqa: E402

BLUE, ORANGE, GREEN, RED = (31, 119, 180), (255, 127, 14), (44, 160, 44), (214, 39, 40)
PANELS = {
    "D": [0.05, 0.04, 0.03, 0.02, 0.01, 0.0],
    "E": [8e-4, 7e-4, 6e-4, 5e-4, 4e-4, 3e-4, 2e-4, 1e-4, 0.0],
    "F": [4e-3, 3e-3, 2e-3, 1e-3, 0.0],
}


LINES = {  # reading -> (panel, colour, seed height as a fraction of the plot from its top, at x = 500)
    "d_array": ("D", BLUE, "0.9"),
    "d_linked": ("D", ORANGE, "0.3"),
    "d_vectorized": ("D", GREEN, "0.75"),
    "e_array": ("E", BLUE, "0.95"),
    "e_linked": ("E", ORANGE, "0.3"),
    "f_array_any": ("F", BLUE, "0.98"),
    "f_array_all": ("F", ORANGE, "0.85"),
    "f_linked_any": ("F", GREEN, "0.85"),
    "f_linked_all": ("F", RED, "0.4"),
}


def read(image, at, panel, colour, seed_x=500, pick="lowest"):
    ax_x, ax_y, box = K.axes(image, PANELS[panel], [200, 400, 600, 800], ylen=12, xlen=12)
    return K.read_traced(image, at, ax_x, ax_y, box, colour, 50, seed_x, pick=pick)


def read_line(image, at, name):
    panel, colour, pick = LINES[name]
    return read(image, at, panel, colour, 500, pick)
