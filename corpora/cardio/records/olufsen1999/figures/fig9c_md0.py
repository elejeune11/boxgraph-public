"""Fig. 9(C) (PDF p. 9): the measured curve md 0 (dash-dot), Mills et al. (ref. 26). See _dashes.py.

y labels matched: 90 at the top frame, -90 at the bottom frame, 0 the major tick between.
For omega 2.8-4.2 md 0 is the upper of the two dash tracks (it starts at omega 2.7, the dashed one
at 1); for omega 8.5-17 it is the upper one again (the flat stretch above the solid line; the
dashed one runs below the solid line).
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_dashes", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_dashes.py"))
_d = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_d)

PLAN = [(2.8, 4.2, 0, 2), (8.5, 17.0, 0, 2)]  # (x from, x to, rank of the track from the top, tracks expected)


def read(image, at):
    return _d.read(image, at, False, 90.0, -90.0, 0.0, PLAN)
