"""Fig. 5 (PDF p. 6): the orange critical branch (lambda = lambda*), kR against d/R, for
lambda_max = 1.1R and r_p = R.

Calibration by _colour_curves.py (see its docstring): labelled y ticks 30, 20, 10 from the top;
x labels 0, 0.2, ... under every second tick (0.1 per tick). The orange (255, 89, 0) pixels fall
into the two long pieces of the branch (cut by the critical-point dot and the green dashes), the
leader line from the label "critical point" with the dot, and the orange letters. The branch is
the parts of at least 30% of the largest part's size, leaving out the part that holds the dot
(the deepest orange pixel); it is not read near the dot (0.53 < d/R < 0.63).
"""
import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi


def _mod():
    spec = importlib.util.spec_from_file_location("haas2015_colour_curves", Path(__file__).with_name("_colour_curves.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    m = _mod()
    cal = m.calibrate(image, [30.0, 20.0, 10.0], 0.1)
    mask, lab, order, sizes = m.colour_parts(cal, (255, 89, 0))
    edt = ndi.distance_transform_edt(mask)
    r, c = np.unravel_index(int(np.argmax(edt)), edt.shape)
    dot = lab[r, c]
    keep = [i for i in order if sizes[i - 1] >= 0.3 * sizes[order[0] - 1] and i != dot]
    branch = np.isin(lab, keep)
    return m.read_mask(cal, branch, at, "orange critical branch")
