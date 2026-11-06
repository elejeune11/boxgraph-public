"""Fig. 9(C) (PDF p. 9): the measured curve md 1 (dashed), Mills et al. (ref. 26). See _dashes.py.

y labels matched: 90 at the top frame, -90 at the bottom frame, 0 the major tick between.
For omega 0.95-2.1 md 1 is the only dash track (md 0 starts at omega 2.7); for omega 2.8-4.2 it
is the lower of two; for omega 6.5-15 it is the lower of two (the flat stretch below the solid line).
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_dashes", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_dashes.py"))
_d = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_d)

PLAN = [(0.95, 2.1, 0, 1), (2.8, 4.2, 1, 2), (6.5, 15.0, 1, 2)]  # (x from, x to, rank from the top, tracks expected)


def read(image, at):
    return _d.read(image, at, False, 90.0, -90.0, 0.0, PLAN)
