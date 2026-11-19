"""Supp. Fig. 1f (PDF p. 23): the dotted slate-blue step line, pre-stress sigma_a, for midline
pre-strain 5.25.

Calibration in _fig2.py; y labels 300, 250, 200, 150, 100, 50, 0, -50 (top to bottom). The line is
the run of its colour (48, 96, 128) near each position; the legend's sample line lies above the
value 275 and is left out.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig2  # noqa: E402


def read(image, at):
    return _fig2.read_line(image, at, [300.0, 250.0, 200.0, 150.0, 100.0, 50.0, 0.0, -50.0], (48, 96, 128),
                           (-45.0, 275.0))
