"""Fig. 4F (PDF p. 9): opening angle Phi against time, red dots (right axis).

Shared code and calibration: _fig4fj.py.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("trushko2020__fig4fj", Path(__file__).with_name("_fig4fj.py"))
M = importlib.util.module_from_spec(_s)
_s.loader.exec_module(M)


def read(image, at):
    return M.read_4f(image, "phi")
