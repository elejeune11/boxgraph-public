"""Fig. 9(B) (PDF p. 9): the measured curve md 1 (dashed), Mills et al. (ref. 26). See _dashes.py.

y labels matched: 10^4 at the top frame, 10^2 at the bottom frame, 10^3 the major tick between.
For omega 6.5-21 md 1 is the lower of the two dash tracks below the solid line (its minimum is
near omega 27); for omega 37-46 it is the upper one.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_dashes", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_dashes.py"))
_d = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_d)

# (x from, x to, rank of the track from the top, tracks expected[, window, grouping]); for 37-46 the
# tracks are far apart but steep: only the dashes at the column itself (narrow window)
PLAN = [(6.5, 21.0, 1, 2), (37.0, 46.0, 0, 2, 0.01, 4.0)]


def read(image, at):
    # the two tracks run about three line widths apart here: a narrower window and grouping
    return _d.read(image, at, True, 1e4, 1e2, 1e3, PLAN, W_frac=0.02, tol=1.5)
