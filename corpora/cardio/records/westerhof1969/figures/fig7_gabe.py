"""Fig. 7: Gabe et al. (1964) in man (dash-dot line): the dot on each error bar and the bar ends.

`at` gives where to look (about every 1 cps); each value is the error bar nearest to it, at the
abscissa read from the image. Stems are searched between C_app = 2.5 and 19 m/sec, which leaves
out the axis captions."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig7 as F  # noqa: E402
import _w69 as W  # noqa: E402


def read(image, at):
    cal = F.calibrate(image)
    return W.read_bars(cal, "v", at, tol_x=0.1, x_from="read", band=(19, 2.5), dot_r=F.DOT_R)
