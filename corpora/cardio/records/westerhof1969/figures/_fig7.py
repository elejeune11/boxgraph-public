"""Fig. 7 (p. 16, printed sideways): apparent wave velocity in the aorta against frequency.

Prototype (thin line, crosses), final model (thick line), Luchsinger et al. 1964 (dashed, dots
with error bars) and Gabe et al. 1964 (dash-dot, dots with error bars), in man.

The crop is turned upright (np.rot90 k=3). The frequency axis has ticks across it, labelled
0 ... 10 (the 0 at the corner, on the ordinate line); the ordinate C_app (m/sec) is labelled
0 ... 20. The window below only says where on the upright crop the ordinate ticks lie.
"""

import _w69 as W

K = 3
X_LABELS = [0, 2, 4, 6, 8, 10]
PANELS = {"v": ([20, 15, 10, 5, 0], (0, 2600))}
BOLD_HALF = 8  # px at 1200 dpi: half-width of the thick (final model) line
DOT_R = 16  # px at 1200 dpi: radius of an isolated data dot (the Gabe dots measure 13-16)


def calibrate(image):
    return W.calibrate(image, K, X_LABELS, PANELS, xtick_side="up", x_zero_at_ordinate=True)
