"""Fig. 2(a): the highest pressure peak in each cycle, which is the femoral artery's (dash-dot line,
its sharp peaks stand clear above the other three lines). See _fig2.py."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_fig2", Path(__file__).with_name("_fig2.py"))
f2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f2)


def read(image, at):
    return f2.peaks(image, "a", [(0.4, 0.7), (1.4, 1.7)], 1.0, 29.5)
