"""Fig. 3, upper-left panel (p. 5): the shallow line through the open circles (4.4 um, Eq. 3 with
the Table 2 B and C). With markers masked, it is the lower of the lines in a column; beyond
H_D = 0.5 only runs above 1.25 are taken, since the panel label '4.4 um n: 96' stands below the
line there. Below H_D = 0.1 the two lines run together and are not read. Calibration in _fig3.py."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig3 as F  # noqa: E402


def band(x):
    if x < 0.1:
        return None
    return (0.8, 3.6, "bottom") if x <= 0.5 else (1.25, 3.6, "bottom")


def read(image, at):
    return F.read_line(image, at, "3.3/4.4", band, "lower line of the panel")
