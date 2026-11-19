"""Shared reading for Fig. 4b (PDF p. 8): furrow apex position against time, simulations (dashed
lines) at transverse planes x = 0, 50, 100, 150 um (gnuplot, see _gp.py).

Calibration: y: the top frame line carries the printed 50 and the major inward ticks on the right
frame line (the mirror of the labelled left ones) 40, 30, 20, 10 (top to bottom); on the left frame
the lines drawn over the ticks at 20 and 0 hide them; the tick at 0 is not used. x: the frame lines carry the printed -4 and 12, the inward ticks -2 to 10.
Colours: each plane has one colour (77% opaque over white): 0 (124, 197, 238), 50 (58, 255, 255),
100 (243, 234, 109), 150 (255, 186, 58). The same colour also draws the measured posterior line
(solid) and, for 50, 100 and 150, the anterior one (dotted). The rows searched for each dashed line
are a band of values that holds it and leaves out the solid and dotted lines of its colour at the
times read (from the image: 0: 1.3-3.6; 50: 3.8-6.5; 100: 8.5-12.8; 150: 21.3-27).
"""
import _gp

COLOURS = {"0": (124, 197, 238), "50": (58, 255, 255), "100": (243, 234, 109), "150": (255, 186, 58)}
ROWS = {"0": (1.3, 3.6), "50": (3.8, 6.5), "100": (8.5, 12.8), "150": (21.3, 27.0)}
SPEC = {"ylabels": [(50.0, "frame-top"), (40.0, "tick:0"), (30.0, "tick:1"), (20.0, "tick:2"), (10.0, "tick:3")],
        "xlabels": [(-4.0, "frame-left")] + [(float(v), f"tick:{k}") for k, v in enumerate(range(-2, 11, 2))]
        + [(12.0, "frame-right")],
        "tol": 30, "win": 40, "yside": "right"}  # +-40 columns bridge a dash gap


def read(image, at, pos):
    return _gp.read_lines(image, at, dict(SPEC, rgb=COLOURS[pos], rows=ROWS[pos]))
