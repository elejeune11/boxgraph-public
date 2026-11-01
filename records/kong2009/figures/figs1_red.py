"""Fig. S1: the red curve (control: tra5b1-Fc, which lacks the 9EG7 epitope)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _s1  # noqa: E402

# the printed y tick labels matched to the ticks found (bottom to top, the unlabelled tick at the x axis
# left out); the decade labels 10^0 ... 10^3 as their exponents; the curve's colour; the legend region
CONFIG = {'y_labels': [0.0057, 0.0114, 0.0171, 0.0228, 0.0285], 'decades': [0, 1, 2, 3], 'colour': 'red', 'exclude': [[0.6, 0, 1, 0.3]]}


def read(image, at):
    return _s1.read_curve(image, at, **CONFIG)
