"""Fig. 6B (PDF p. 12): angle against delta/R, dark grey dots (simulation means).

Shared code and calibration: _fig6.py.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("trushko2020__fig6", Path(__file__).with_name("_fig6.py"))
M = importlib.util.module_from_spec(_s)
_s.loader.exec_module(M)


def read(image, at):
    return M.read(image, at, "6B", "simmean")
