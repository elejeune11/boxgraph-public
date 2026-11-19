"""Fig. 4J (PDF p. 9): spring constant of 2.5% capsules with a monolayer, red dots, x = rank.

Shared code and calibration: _fig4fj.py.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("trushko2020__fig4fj", Path(__file__).with_name("_fig4fj.py"))
M = importlib.util.module_from_spec(_s)
_s.loader.exec_module(M)


def read(image, at):
    return M.read_4j(image, "tissue")
