"""Fig. S5F (PDF p. 27): mean capsule thickness against time, one capsule, open circles, SD bars.

Shared code and calibration: _figs5.py.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("trushko2020__figs5", Path(__file__).with_name("_figs5.py"))
M = importlib.util.module_from_spec(_s)
_s.loader.exec_module(M)


def read(image, at):
    return M.read_panel(image, "F")
