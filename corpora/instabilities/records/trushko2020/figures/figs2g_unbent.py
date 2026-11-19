"""Fig. S2G (PDF p. 24): mean normalised intensity against time, unbent lumen (blue).

Shared code and calibration: _figs2.py.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("trushko2020__figs2", Path(__file__).with_name("_figs2.py"))
M = importlib.util.module_from_spec(_s)
_s.loader.exec_module(M)


def read(image, at):
    return M.read_curve(image, at, "G", "unbent")
