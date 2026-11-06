"""Fig. 6 (p. 16, printed sideways): input impedance of the whole model (bold solid line) and
measurements in man: Patel et al. 1965 (dots), Patel et al. 1964 (open circles), Gabe et al.
1964 (crosses). R = 1420.

The crop is turned upright (np.rot90 k=3); the frequency axis is the phase panel's (ticks
pointing into the plot, labelled 0 ... 14); the modulus ordinate |Z_in|/R x 100 is labelled
0 ... 25, the phase ordinate -75 ... 75. The windows below only say where on the upright crop
each panel's ordinate ticks lie.
"""

import _w69 as W

K = 3
X_LABELS = [2, 4, 6, 8, 10, 12, 14]
PANELS = {"mod": ([25, 20, 15, 10, 5, 0], (0, 2500)),
          "ph": ([75, 50, 25, 0, -25, -50, -75], (2550, 4180))}
BOLD_HALF = 8  # px: half-width of the model line at 900 dpi; the measured lines are about half


def calibrate(image):
    return W.calibrate(image, K, X_LABELS, PANELS, xtick_side="up")
