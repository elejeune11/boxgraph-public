"""Fig. S6H (PDF p. 28): delta/R against Delta eps, common envelope (10^8 curve).

Shared code and calibration: _figs6.py.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("trushko2020__figs6", Path(__file__).with_name("_figs6.py"))
M = importlib.util.module_from_spec(_s)
_s.loader.exec_module(M)


def read(image, at):
    return M.read_envelope(image, "H", at)
