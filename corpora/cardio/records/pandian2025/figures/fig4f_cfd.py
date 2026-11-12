"""Fig. 4f (p. 8): the black central line and grey whiskers of the three CFD columns (IL1beta-1-CFD, -2-CFD,
-3-CFD); x = network 1, 2, 3 (categories 2, 4, 6). Log axis 10^0 ... 10^3 um/s. See _cols.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_pairs", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_pairs.py"))
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)


def read(image, at):
    return P.read_pair(image, at, (400, 2450, 50, 2000), [3, 2, 1, 0], "cfd", 0.13)
