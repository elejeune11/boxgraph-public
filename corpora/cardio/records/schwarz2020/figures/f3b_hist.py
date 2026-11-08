"""Fig. 3B (p. 7): the histogram bars (frequency per symmetry bin of width 0.05) for mother diameter 75-90 um (blue), read at the bin centres. Calibration and reading rules in _boxfigs.py and _sz.py."""
import importlib.util
import os

_s = importlib.util.spec_from_file_location("schwarz2020_boxfigs", os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "_boxfigs.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)


def read(image, at):
    return B.fig3(image, at, (48, 132, 188))
