"""Fig. 5D (p. 9): the brown line 'cast, median' (reconstructed heart with extrapolated microcirculation). Code and reading rules in _f5.py; y labels [0, 20, 40, 60, 80, 100, 120, 140]."""
import importlib.util
import os

_s = importlib.util.spec_from_file_location("schwarz2020_f5", os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "_f5.py"))
F = importlib.util.module_from_spec(_s)
_s.loader.exec_module(F)


def read(image, at):
    return F.read_line(image, at, [1, 10, 100, 1000, 10000], [0, 20, 40, 60, 80, 100, 120, 140], False, 'brown')
