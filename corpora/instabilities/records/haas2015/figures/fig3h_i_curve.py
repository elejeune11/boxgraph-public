"""Fig. 3(h) (PDF p. 4), second reading: the thick solid curve Delta beta^(i) / cos Theta (in units
of d/delta) against lambda/delta. Calibration and curve finding by _fig3_core.py (see its
docstring); the labelled y ticks are 0.4, 0.2 and 0, from the top. The curve is found by its
thickness, so it is read also where it meets the dashed line or runs along the x axis.
"""
import importlib.util
from pathlib import Path


def _mod():
    spec = importlib.util.spec_from_file_location("haas2015_fig3_core", Path(__file__).with_name("_fig3_core.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    return _mod().read_curve(image, at, [0.4, 0.2, 0.0], "thick solid curve, middle of its core")
