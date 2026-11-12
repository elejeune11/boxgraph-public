"""Fig. 3f (p. 6): the black central line and grey whiskers of the three 'CFD' columns of the control
networks; x = network 1, 2, 3 (categories 2, 4, 6). Log axis 10^0 ... 10^4 um/s. See _cols.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_pairs", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_pairs.py"))
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)


def read(image, at):
    return P.read_pair(image, at, (300, 2300, 20, 1750), [4, 3, 2, 1, 0], "cfd", 0.15)
