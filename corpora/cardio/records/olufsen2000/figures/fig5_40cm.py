"""Fig. 5 (PDF p. 12): simulated aortic pressure 40 cm along the aorta, the solid line '40 cm'.

The solid line is found as in _fig7.py (dark runs that can be followed for 6 t columns; the dashed,
dotted and dash-dotted lines of 10, 20 and 30 cm break up sooner). Where the four lines run together
the reading column holds a merged run or more than one solid run; those positions are left out of `at`,
and so are 3.3875 and 3.55-3.5875 s, where the overlay showed the run taking in the converging
10-30 cm lines.

Frame: in this panel the legend's lower edge lies on the 110 mmHg grid line, so together they make a
long dark row in the upper half, which _common.frame would take for the top frame. Here the frame is
the outermost long dark rows and columns instead (a private copy of _common with that frame finder;
the shared file is unchanged).
Labels matched: x ticks 3.4, 3.6, 3.8, 4, 4.2, 4.4 s; y: bottom frame 80 mmHg, interior ticks
120, 110, 100, 90 mmHg (top frame unlabelled)."""
import importlib.util
import os

import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(name[:-3] + "_fig5", os.path.join(_here, name))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_c = _load("_common.py")


def _frame_outer(g):
    dark = g < 0.5 * (np.median(g) + np.percentile(g, 0.5))
    rows, cols = dark.sum(1), dark.sum(0)
    rr = np.where(rows > 0.6 * rows.max())[0]
    cc = np.where(cols > 0.6 * cols.max())[0]
    # the inner edge of the outermost line groups
    top = int(_c.groups(list(rr))[0][-1])
    bot = int(_c.groups(list(rr))[-1][0])
    left = int(_c.groups(list(cc))[0][-1])
    right = int(_c.groups(list(cc))[-1][0])
    return top, bot, left, right, dark


_c.frame = _frame_outer
_f = _load("_fig7.py")
_f._c = _c


def read(image, at):
    return _f.read_sim(image, at, (None, 80.0), [120.0, 110.0, 100.0, 90.0],
                       [3.4, 3.6, 3.8, 4.0, 4.2, 4.4])
