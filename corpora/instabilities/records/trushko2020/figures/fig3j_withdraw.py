"""Fig. 3J (PDF p. 7): force against indentation depth, the blue withdraw curve.

Shared code and calibration: _fig3j.py.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("trushko2020__fig3j", Path(__file__).with_name("_fig3j.py"))
M = importlib.util.module_from_spec(_s)
_s.loader.exec_module(M)


def read(image, at):
    return M.read_curve(image, at, "withdraw")
