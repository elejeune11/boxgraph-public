"""Fig. 3a (PDF p. 7): the solid orange line, MuVi SPIM apical area fold change of the ventral region
(five rows from the midline, mean of the embryos) against time. Calibration in _fig3a.py; colour
(255, 192, 32). Where the confocal (red) and simulated (blue) lines are drawn over it, only the
orange pixels left visible are used; a position where none is visible is not read.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig3a  # noqa: E402


def read(image, at):
    return _fig3a.read(image, at, (255, 192, 32), (0.3, 1.05))
