"""Fig. 4f (PDF p. 8): the solid cyan line 'Along AP: Simulations'.
Calibration in _fig4f.py; the legend's sample line (about -0.044) lies outside the rows searched.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig4f  # noqa: E402


def read(image, at):
    return _fig4f.line(image, at, _fig4f.CYAN, (-0.003, 0.007))
