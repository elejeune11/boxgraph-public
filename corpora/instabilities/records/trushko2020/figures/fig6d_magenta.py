"""Fig. 6D (PDF p. 12): mean simulated pressure against cell number, k^s 0.01 c^b 0.02.

Shared code and calibration: _fig6.py.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("trushko2020__fig6", Path(__file__).with_name("_fig6.py"))
M = importlib.util.module_from_spec(_s)
_s.loader.exec_module(M)


def read(image, at):
    return M.read(image, at, "6D", "magenta")
