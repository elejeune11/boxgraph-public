"""Fig. 4f (PDF p. 8): the dashed navy line 'Along DV: Simulations'.
Calibration in _fig4f.py; dashes read over +-20 columns; the legend's sample line (about -0.0535)
lies outside the rows searched. The MuVi band is drawn over the line at 25% opacity, so where the
band lies the navy (0, 0, 139) shows as (48, 32, 104): the colour searched is the middle of the two,
(24, 16, 121), with a tolerance (50) that takes both and leaves out the goldenrod lines.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig4f  # noqa: E402


def read(image, at):
    return _fig4f.line(image, at, (24, 16, 121), (-0.047, 0.0125), win=20)
