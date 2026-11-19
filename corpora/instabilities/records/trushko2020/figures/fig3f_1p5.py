"""Fig. 3F (PDF p. 7): capsule pressure (Pa) against time, 1.5% alginate (red dots, SEM band).

Shared code and calibration: _fig3df.py.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("trushko2020__fig3df", Path(__file__).with_name("_fig3df.py"))
M = importlib.util.module_from_spec(_s)
_s.loader.exec_module(M)


def read(image, at):
    return M.read_series(image, "3F", "1.5")
