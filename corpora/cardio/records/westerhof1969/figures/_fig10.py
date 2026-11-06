"""Fig. 10, left (p. 20, printed sideways): |Z_in| and phase of the model for the clinical cases.

The bold solid line is case (a), normal: R = 1420. The crop is turned upright (np.rot90 k=3);
the frequency axis is the phase panel's (ticks pointing into the plot, labelled 0 ... 12); the
modulus ordinate is labelled 0 ... 500, the phase ordinate -75 ... 25. The windows below only say
where on the upright crop each panel's ordinate ticks lie.
"""

import _w69 as W

K = 3
X_LABELS = [2, 4, 6, 8, 10, 12]
PANELS = {"mod": ([500, 400, 300, 200, 100, 0], (0, 1900)),
          "ph": ([25, 0, -25, -50, -75], (2100, 2950))}
BOLD_R = 7  # px: thin lines are about 9 px wide at 900 dpi, the bold line about twice that


def calibrate(image):
    return W.calibrate(image, K, X_LABELS, PANELS, xtick_side="up")
