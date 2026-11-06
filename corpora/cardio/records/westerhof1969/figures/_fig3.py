"""Fig. 3 (p. 11): |Z_in| and phase of the whole tree against frequency, curves a-e.

The bold line is e (NEW RADII, the final model). Both panels share the frequency axis at the
bottom (ticks pointing up, labelled 2 ... 12). The modulus ordinate is labelled 0 ... 400, the
phase ordinate -75 ... 25; the windows below only say where on the crop each panel's ticks lie.
"""

import _w69 as W

X_LABELS = [2, 4, 6, 8, 10, 12]
PANELS = {"mod": ([400, 300, 200, 100, 0], (0, 1950)),
          "ph": ([25, 0, -25, -50, -75], (2000, 3100))}
BOLD_R = 8  # px: thin lines are 9-12 px wide at 900 dpi, the bold line about twice that


def calibrate(image):
    return W.calibrate(image, 0, X_LABELS, PANELS, xtick_side="up")
