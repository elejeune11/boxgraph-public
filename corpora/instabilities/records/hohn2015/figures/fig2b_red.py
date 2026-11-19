"""Fig. 2(b) (PDF p. 2): A/A0 against t (minutes) for the representative embryo (red line with
open circles at the times of the traced shapes).

Calibration by _fig2.py: x ticks every 10 min as in (a). The y label 1.5 is printed level with
the top line of the box, so that line is the mark 1.5; the ticks labelled 1.0 and 0.5 are found
on whichever side shows them (the ticks on the right are lost under the embryo lines at this
resolution, and the left 1.0 tick is crossed by them), taken from the bottom up.
"""
import importlib.util
from pathlib import Path


def _mod():
    spec = importlib.util.spec_from_file_location("hohn2015_fig2", Path(__file__).with_name("_fig2.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    return _mod().read_red(image, at, [-20, -10, 0, 10, 20, 30, 40], [0.5, 1.0], y_frame=(1.5, None))
