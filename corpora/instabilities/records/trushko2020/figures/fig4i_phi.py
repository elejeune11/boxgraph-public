"""Fig. 4I (PDF p. 9): the blue dots, measured opening angle Phi against P_B R^3 (n = 14).

Shared code in _fig4.py: blue blobs inside the axes; the legend dot (top fifth of the plot) is left
out; one blob twice the usual area (two dots overlapping near P_B R^3 = 54) is split along its long
axis. No error bars are drawn. Interval: 3 px on a dot's centre (half a dot radius for each of the
two split dots, whose centres are less certain) plus twice the calibration misfit.
"""
import importlib.util
from pathlib import Path


def _mod():
    spec = importlib.util.spec_from_file_location("trushko2020_fig4", Path(__file__).with_name("_fig4.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    m = _mod()
    return m.read_markers(image, m.BLUE, 50.0, 10.0, 0.2)
