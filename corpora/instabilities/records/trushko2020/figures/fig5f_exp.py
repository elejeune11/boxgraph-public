"""Fig. 5F (PDF p. 11): histogram of fold number, experiment (dark green bars).

Shared code and calibration: _fig5f.py.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("trushko2020__fig5f", Path(__file__).with_name("_fig5f.py"))
M = importlib.util.module_from_spec(_s)
_s.loader.exec_module(M)


def read(image, at):
    return M.read_hist(image, "exp")
