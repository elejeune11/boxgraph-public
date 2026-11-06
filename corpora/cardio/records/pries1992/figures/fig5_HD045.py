"""Fig. 5 (p. 6): the solid line labelled H_D 0.45 (Eq. 2 at 0.45, as Fig. 2). Calibration and line finding in _fig5.py; the value bands below keep
the line apart from the two broken lines, the letters near the minimum and the curve label below it."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig5 as F  # noqa: E402

# x as printed in `at`: (lowest, highest calibrated value of the run's centre, which run in the band)
BANDS = {'3.3': (3.0, 4.4, 'top'), '4': (2.0, 2.45, 'top'), '4.5': (1.65, 1.85, 'top'), '25': (1.5, 1.9, 'top'), '50': (1.9, 2.3, 'top'), '200': (2.6, 3.0, 'top'), '250': (2.7, 3.1, 'top'), '300': (2.8, 3.1, 'top'), '500': (3.0, 3.3, 'top'), '700': (3.05, 3.35, 'top'), '1200': (3.1, 3.4, 'top'), '1500': (3.1, 3.4, 'top'), '2000': (3.1, 3.4, 'top'), '2300': (3.1, 3.4, 'top')}


def read(image, at):
    return F.read_bands(image, at, BANDS, "solid line")
