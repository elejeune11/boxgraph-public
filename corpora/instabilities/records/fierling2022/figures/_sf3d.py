"""Shared calibration for Supp. Fig. 3d (PDF p. 25): ventral furrow apex z position against time at
eight AP positions, MuVi SPIM, n = 6 embryos (gnuplot, see _gp.py). Each line is the median over
embryos (caption: 'Lines represent medians'), drawn over its shaded min-max band.

y: the frame lines carry the printed 60 (top) and 0 (bottom); the major inward ticks on the left
frame line 50, 40, 30, 20, 10. x: the frame lines carry the printed -4 and 12; the inward ticks -2 to
10 (the bottom ones are partly under the bands: the mirrored ticks on the top frame line are used
when the bottom ones are not all seen).
The bands (50% opaque) are drawn over the left ticks and turn their black into a dark tint of the
band's colour: within 60 px inside the left frame line, pixels darker than mean 110 are set to black
before calibrating (band interiors, a mix with white, stay light). Data lines that are this dark and
touch the frame (the black, green and dark-blue lines) then give runs as long as the search depth;
runs of 60 px or more are not taken as ticks (the ticks are about 30 px long).
Lines: gnuplot's default line types 1-8, drawn on top of all bands, read by _gp.read_lines.
"""
import numpy as np

import _gp

COLOURS = {"-150": (148, 0, 211), "-100": (0, 158, 115), "-50": (86, 180, 233), "0": (230, 159, 0),
           "50": (240, 228, 66), "100": (0, 114, 178), "150": (229, 30, 16), "200": (0, 0, 0)}
SPEC = {"ylabels": [60.0, 50.0, 40.0, 30.0, 20.0, 10.0, 0.0],
        "xlabels": [(-4.0, "frame-left")] + [(float(v), f"tick:{k}") for k, v in enumerate(range(-2, 11, 2))]
        + [(12.0, "frame-right")],
        "tol": 45, "win": 10, "rows": (-1.0, 49.0), "tick_max": 60}  # the legend's samples lie above 51


def _restore_ticks(image):
    img = image.copy()
    fr = _gp.frame(img)
    f = img.astype(float)
    dark = f.mean(axis=2) < 110
    c0 = int(fr["left_in"])
    sub = dark[:, c0:c0 + 60]
    block = img[:, c0:c0 + 60]
    block[sub] = 0
    return np.asarray(img)


# Two line colours lie close to colours that overlapping 50% bands make (the light-blue line to the
# dark-blue band over white, the yellow line to the yellow band over the orange band): those two are
# searched with a tolerance of 18 instead of 45.
TOL = {"-50": 18, "50": 18}


def read(image, at, pos):
    return _gp.read_lines(_restore_ticks(image), at, dict(SPEC, rgb=COLOURS[pos], tol=TOL.get(pos, 45)))
