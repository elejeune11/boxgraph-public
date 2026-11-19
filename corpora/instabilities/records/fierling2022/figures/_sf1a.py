"""Shared calibration for Supp. Fig. 1a (PDF p. 23), main panel: AP and DV stress at the ventral
midline against the pre-stress (gnuplot, see _gp.py).

y: the frame lines carry the printed 3000 (top) and 0 (bottom); the major inward ticks on the left
frame line between them 2500, 2000, 1500, 1000, 500. x: the left frame line carries 0, the right one
1500, the two major inward ticks 500 and 1000 (the short ticks between are minor). The inset (its
frame is shorter than the main frame's sides, which are the longest dark lines) lies above the value
1700 for pre-stress below about 1050: the rows searched stay below it, and below the legend.
"""
import _gp

SPEC = {"ylabels": [3000.0, 2500.0, 2000.0, 1500.0, 1000.0, 500.0, 0.0],
        "xlabels": [(0.0, "frame-left"), (500.0, "tick:0"), (1000.0, "tick:1"), (1500.0, "frame-right")],
        "tol": 60, "win": 8, "rows": (-40.0, 1680.0)}


def read(image, at, rgb):
    return _gp.read_lines(image, at, dict(SPEC, rgb=rgb))
