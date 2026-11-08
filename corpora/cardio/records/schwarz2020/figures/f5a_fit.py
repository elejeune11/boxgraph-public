"""Fig. 5A (p. 9): the black line 'cast, fit' (the allometric fit on the reconstructed heart). Code and reading rules in _f5.py; y labels [10.0 ** k for k in range(-6, 2)]."""
import importlib.util
import os

_s = importlib.util.spec_from_file_location("schwarz2020_f5", os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "_f5.py"))
F = importlib.util.module_from_spec(_s)
_s.loader.exec_module(F)


def read(image, at):
    return F.read_line(image, at, [1, 10, 100, 1000, 10000], [10.0 ** k for k in range(-6, 2)], True, 'black')
