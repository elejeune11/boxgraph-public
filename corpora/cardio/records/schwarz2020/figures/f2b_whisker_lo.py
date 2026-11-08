"""Fig. 2B (p. 6): the left whisker end of the segment-length box plot of each diameter class (classes by their lower bound, 30-45 ... >=400 um). Calibration and reading rules in _boxfigs.py and _sz.py."""
import importlib.util
import os

_s = importlib.util.spec_from_file_location("schwarz2020_boxfigs", os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "_boxfigs.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)


def read(image, at):
    return B.fig2b(image, at, 'whisker_lo')
