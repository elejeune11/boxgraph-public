"""Fig. 6 (p. 10): the lower whisker end of the perfusion box plot of each region (1 LV epi, 2 LV mid, 3 LV endo, 4 Sept LV, 5 Sept mid, 6 Sept RV). Calibration and reading rules in _boxfigs.py and _sz.py."""
import importlib.util
import os

_s = importlib.util.spec_from_file_location("schwarz2020_boxfigs", os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "_boxfigs.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)


def read(image, at):
    return B.fig6(image, at, 'whisker_lo')
