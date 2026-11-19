"""Fig. 4H (PDF p. 9): the purple curve, gamma against delta/R (theory, lambda R^2/K = 10^8).

Shared code in _fig4.py. The purple legend line lies lower right, below the curve, so the
topmost purple run in a column is taken.
"""
import importlib.util
from pathlib import Path


def _mod():
    spec = importlib.util.spec_from_file_location("trushko2020_fig4", Path(__file__).with_name("_fig4.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    m = _mod()
    return m.read_curve(image, at, m.PURPLE, 0.25, 10.0, pick="top", core=True)
