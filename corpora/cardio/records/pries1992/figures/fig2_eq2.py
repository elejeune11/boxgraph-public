"""Fig. 2 (p. 4): the broken fitting line of Eq. 2 (eta_rel at hematocrit 0.45 against tube
diameter). The figure has the layout of Fig. 5, so the calibration and line finding of _fig5.py
are used, with the y ticks of this figure: every 0.5 from 4.5 (top frame, unlabelled) down to 1
(labelled 4 -- printed like '+' -- 3, 2, 1). The line is read only where it stands clear of the
data letters and the lines joining them: on its steep descent below the letter Z (D 3.3-4.2) and
beyond the last data letters (D > 1,200 um), where it is the lowest run between 3.05 and 3.35 (the
thin line joining the letters C runs just above it up to about 1,700 um)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig5 as F  # noqa: E402

Y_LABELS = [4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0]
BANDS = {"3.3": (2.5, 4.4, "top"), "3.6": (2.2, 4.0, "top"), "4": (1.6, 3.2, "top"),
         "1200": (3.05, 3.35, "bottom"), "1500": (3.05, 3.35, "bottom"), "2000": (3.05, 3.35, "bottom"),
         "2300": (3.05, 3.35, "bottom")}


def read(image, at):
    return F.read_bands(image, at, BANDS, "broken line of Eq. 2", y_labels=Y_LABELS)
