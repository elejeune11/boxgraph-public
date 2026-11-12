"""Fig. 3i (p. 6), "Interstitial space velocity in the networks": the black central line of each control
network (x = 1, 2, 3). No whiskers. Log axis 10^3 ... 10^0 um/s. See _cols.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_cols", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cols.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def read(image, at):
    cal = C.calibrate(image, (300, 2200, 20, 1900), [3, 2, 1, 0], True)
    return C.read_column(image, at, cal)
