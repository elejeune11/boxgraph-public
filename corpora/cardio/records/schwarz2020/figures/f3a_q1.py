"""Fig. 3A (p. 7): the left box edge (25th percentile) of the daughter-symmetry box plot of each mother diameter class (classes by their lower bound). Calibration and reading rules in _boxfigs.py and _sz.py."""
import importlib.util
import os

_s = importlib.util.spec_from_file_location("schwarz2020_boxfigs", os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "_boxfigs.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)


def read(image, at):
    return B.fig3a(image, at, 'q1')
