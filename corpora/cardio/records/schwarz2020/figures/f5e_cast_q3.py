"""Fig. 5E (p. 9): the upper edge of the brown area 'cast, IQR' (75th percentile). Code and reading rules in _f5.py; y labels [0, 4, 8, 12, 16, 20]."""
import importlib.util
import os

_s = importlib.util.spec_from_file_location("schwarz2020_f5", os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "_f5.py"))
F = importlib.util.module_from_spec(_s)
_s.loader.exec_module(F)


def read(image, at):
    return F.read_edge(image, at, [1, 10, 100, 1000, 10000], [0, 4, 8, 12, 16, 20], False, 'tan', 'upper')
