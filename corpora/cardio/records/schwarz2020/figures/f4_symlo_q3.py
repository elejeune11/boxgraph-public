"""Fig. 4 (p. 8): the upper box edge (75th percentile) of the area-growth box plot, daughter symmetry 0.0-0.5 (dark boxes), per mother diameter class (by lower bound). Calibration and reading rules in _boxfigs.py and _sz.py."""
import importlib.util
import os

_s = importlib.util.spec_from_file_location("schwarz2020_boxfigs", os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "_boxfigs.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)


def read(image, at):
    return B.fig4(image, at, 'q3', 'dark')
