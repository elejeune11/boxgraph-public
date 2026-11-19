"""Fig. S6C (PDF p. 28): normalised buckling pressure of the five lines, at kR^2/lambda = 100, x = lambda R^2/K.

Shared code and calibration: _figs6.py.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("trushko2020__figs6", Path(__file__).with_name("_figs6.py"))
M = importlib.util.module_from_spec(_s)
_s.loader.exec_module(M)


def read(image, at):
    return M.read_lines(image, "C")
