"""Fig. 2c (PDF p. 5): the dashed navy step line, DV stress sigma_DV, for midline pre-strain 0.43.

Calibration in _fig2.py; y labels 25, 20, 15, 10, 5, 0. The line is the run of its colour
(0, 0, 139) near each position (the window spans more than one dash); the legend's sample line
lies above 22.6 and is left out.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig2  # noqa: E402


def read(image, at):
    return _fig2.read_line(image, at, [25.0, 20.0, 15.0, 10.0, 5.0, 0.0], (0, 0, 139), (-1.0, 22.6))
