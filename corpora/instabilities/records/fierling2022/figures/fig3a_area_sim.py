"""Fig. 3a (PDF p. 7): the solid blue line, simulated apical area fold change of the ventral region
(five rows from the midline) against time. Calibration in _fig3a.py; colour (0, 0, 255); the
legend's sample line (left, value about 0.64) is outside the positions read.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig3a  # noqa: E402


def read(image, at):
    return _fig3a.read(image, at, (0, 0, 255), (0.3, 1.05))
