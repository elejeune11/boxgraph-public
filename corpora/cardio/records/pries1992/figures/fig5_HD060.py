"""Fig. 5 (p. 6): the broken line labelled H_D 0.60 (upper broken line). Calibration and line finding in _fig5.py; the value bands below keep
the line apart from the 0.45 line and the data letters below it, the legend above it, and the thin lines of the G data."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig5 as F  # noqa: E402

# x as printed in `at`: (lowest, highest calibrated value of the run's centre, which run in the band)
BANDS = {'3.6': (2.9, 4.4, 'top'), '4': (2.4, 3.2, 'top'), '4.5': (1.85, 2.3, 'top'), '5': (1.55, 1.75, 'top'), '7': (1.28, 1.45, 'top'), '150': (3.7, 4.3, 'top'), '200': (3.9, 4.5, 'top'), '250': (4.2, 4.6, 'top'), '300': (4.3, 4.7, 'top'), '1000': (4.78, 5.2, 'top'), '1500': (4.78, 5.2, 'top'), '2000': (4.78, 5.2, 'top'), '2300': (4.78, 5.2, 'top')}


def read(image, at):
    return F.read_bands(image, at, BANDS, "upper broken line")
