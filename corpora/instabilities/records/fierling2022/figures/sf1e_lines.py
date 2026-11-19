"""Supp. Fig. 1e (PDF p. 23): the strain profile for midline pre-strain 5.25, three step lines:
'Target size, AP and DV' (dotted steel blue), 'Actual DV size' (dashed navy), 'Actual AP size'
(solid cyan). Calibration in _fig2a.py: top frame 1.1, the reference line 1, inward ticks 0.9 to 0.2,
bottom frame 0.1. The bands here are pi/80 wide: the first band's centre is about 0.0196 rad.
Each reading module below picks one colour.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig2a  # noqa: E402

Y = [(1.1, "frame-top"), (1.0, "hline")] + [(round(0.9 - 0.1 * k, 1), f"tick:{k}") for k in range(8)] + \
    [(0.1, "frame-bottom")]


def read_colour(image, at, rgb, rows, win=8):
    return _fig2a.read_line(image, at, Y, rgb, rows, win=win)
