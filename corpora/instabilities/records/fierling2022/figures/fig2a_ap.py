"""Fig. 2a (PDF p. 5): the solid cyan step line 'Actual AP size' (midline pre-strain 0.43).
Calibration as in fig2a_target.py; colour (0, 238, 238).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig2a  # noqa: E402
from fig2a_target import Y  # noqa: E402


def read(image, at):
    return _fig2a.read_line(image, at, Y, _fig2a.DCYAN, (0.97, 1.02))
