"""Fig. 3D (PDF p. 7): normalised capsule thickness against time, 2.5% alginate (orange dots, SEM band).

Shared code and calibration: _fig3df.py.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("trushko2020__fig3df", Path(__file__).with_name("_fig3df.py"))
M = importlib.util.module_from_spec(_s)
_s.loader.exec_module(M)


def read(image, at):
    return M.read_series(image, "3D", "2.5")
