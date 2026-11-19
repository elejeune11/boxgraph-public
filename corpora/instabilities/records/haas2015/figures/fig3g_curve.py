"""Fig. 3(g) (PDF p. 4), second reading: the solid curve k / (d^1/2 delta^-3/2 sin^1/2 Theta)
against lambda/delta. Calibration and curve finding by _fig3_core.py (see its docstring); the
labelled y ticks are 4 and 3, from the top.
"""
import importlib.util
from pathlib import Path


def _mod():
    spec = importlib.util.spec_from_file_location("haas2015_fig3_core", Path(__file__).with_name("_fig3_core.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    return _mod().read_curve(image, at, [4.0, 3.0], "solid curve, middle of its thick core")
