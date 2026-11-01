"""Fig. 4 C (PDF p. 5): mean traction stress of four characteristic cells, one coloured line with
markers per condition (CONTROL red diamonds, BLEB green circles, CA-RAC blue triangles, CA-RHO
black squares), against cell edge distance (left panel) or F-actin speed (right panel).

The markers are read (the data points); the lines joining them are removed by an opening.
Calibration as in _dots.py (ticks on both edges; long ticks labelled). The legend, inside the
left panel, has one marker per colour followed by its label: a marker with a run of dark text
(many dark pixels) just to its right is a legend entry and is dropped.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("gardel_dots", Path(__file__).with_name("_dots.py"))
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)
L = D.L

OPEN_R = {"red": 11, "green": 11, "blue": 11, "black": 11}


def is_legend(img, p):
    g = L.gray(img)
    r, c = int(p["r"]), int(p["c"])
    win = g[max(0, r - 30):r + 30, c + 90:c + 500]
    return (win < 100).sum() > 4000


def read_colour(img, colour, xv, xstep, yv, ystep, what):
    if colour == "black":
        mask = L.neutral_dark(img, 100)
    else:
        mask = L.hue_mask(img, colour, min_sat=60)
    # markers are apart along each line: each blob that survives an opening wider than the line
    # and is about one marker in size (filling at least 40% of its box: diamonds and triangles
    # fill half) is one marker; a marker merged with another colour's is lost, not guessed
    return D.read_markers(img, mask, xv, xstep, yv, ystep, open_r=OPEN_R[colour], margin=3, what=what,
                          shape="blob", exclude=is_legend, min_fill=0.4, single_from="median")
