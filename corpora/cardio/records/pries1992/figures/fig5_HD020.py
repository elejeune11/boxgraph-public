"""Fig. 5 (p. 6): the broken line labelled H_D 0.20 (lower broken line). Calibration and line finding in _fig5.py; the value bands below keep
the line apart from the letters T, H, U, J, E and the thin lines joining them, and the curve label below it."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig5 as F  # noqa: E402

# x as printed in `at`: (lowest, highest calibrated value of the run's centre, which run in the band)
BANDS = {'3.1': (2.4, 3.0, 'top'), '7': (1.0, 1.2, 'bottom'), '25': (1.1, 1.3, 'top'), '300': (1.5, 1.8, 'top'), '500': (1.6, 1.8, 'top'), '700': (1.64, 1.76, 'top'), '1000': (1.64, 1.76, 'top'), '1200': (1.64, 1.76, 'top'), '1500': (1.64, 1.76, 'top'), '2000': (1.64, 1.76, 'top')}


def read(image, at):
    return F.read_bands(image, at, BANDS, "lower broken line")
