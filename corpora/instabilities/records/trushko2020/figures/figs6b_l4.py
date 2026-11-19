"""Fig. S6B (PDF p. 28): normalised pressure against Delta eps/Delta eps_c, line for lambda R^2/K = 10^4.

Shared code and calibration: _figs6.py.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("trushko2020__figs6", Path(__file__).with_name("_figs6.py"))
M = importlib.util.module_from_spec(_s)
_s.loader.exec_module(M)


def read(image, at):
    return M.read_lines(image, "B", 4, at)
