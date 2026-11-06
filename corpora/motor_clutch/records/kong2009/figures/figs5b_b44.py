"""Fig. S5 B: the blue open circles (44 pN), those that stand clear of the cluster."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _s5  # noqa: E402

# the printed tick labels matched to the ticks found (y bottom to top; x left to right, the unlabelled
# minor ticks taking the values between); the series' colour; a rough ring radius in pixels; the
# legend and title region (fractions of the crop) not searched
CONFIG = {'y_labels': [0, 1, 2, 3, 4, 5], 'x_labels': [0, 20, 40, 60, 80], 'colour': 'blue', 'r_px': 32, 'exclude': [[0.65, 0, 1, 0.65]]}


def read(image, at):
    return _s5.read_rings(image, at, **CONFIG)
