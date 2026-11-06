"""Fig. 5 (p. 13, printed sideways): input impedance of a whole leg in the model (bold line) and
Patel et al. 1965 in man (thin lines with dots, individual subjects), |Z_in|/R x 100, with
R = 16.8 x 10^3.

The crop is turned upright (np.rot90 k=3); the frequency axis is the phase panel's (ticks
pointing into the plot, labelled 0 ... 12); the modulus ordinate is labelled 0 ... 50, the phase
ordinate -75 ... 75. The windows below only say where on the upright crop each panel's ordinate
ticks lie.
"""

import _w69 as W

K = 3
X_LABELS = [0, 2, 4, 6, 8, 10, 12]  # the 0 is printed at the corner, on the ordinate line
PANELS = {"mod": ([50, 40, 30, 20, 10, 0], (0, 2780)),
          "ph": ([75, 50, 25, 0, -25, -50, -75], (2800, 4450))}
BOLD_HALF = 9  # px: half-width of the model line at 900 dpi; the measured lines are thinner


def calibrate(image):
    return W.calibrate(image, K, X_LABELS, PANELS, xtick_side="up", x_zero_at_ordinate=True)
