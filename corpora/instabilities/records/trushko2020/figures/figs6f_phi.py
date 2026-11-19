"""Fig. S6F (PDF p. 28): opening angle Phi against monolayer length, orange dots.

Shared code and calibration: _figs6.py.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("trushko2020__figs6", Path(__file__).with_name("_figs6.py"))
M = importlib.util.module_from_spec(_s)
_s.loader.exec_module(M)


def read(image, at):
    return M.read_4f_like(image, "phi")
