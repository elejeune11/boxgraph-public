"""Fig. 4f (PDF p. 8): the dashed dark-goldenrod line 'Along DV: MuVi SPIM' (mean of n = 6 embryos)
and its shaded band (minimum and maximum over embryos), read through the line's centre.
Calibration in _fig4f.py; dashes read over +-30 columns; the legend's sample line (about -0.0505)
lies outside the rows searched.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig4f  # noqa: E402


def read(image, at):
    return _fig4f.line(image, at, _fig4f.DGOLD, (-0.047, 0.0125), win=30, band=_fig4f.BAND_DV)
