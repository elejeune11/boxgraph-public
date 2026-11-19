"""Fig. 4H (PDF p. 9): the green curve, alpha against delta/R (theory, lambda R^2/K = 10^8).

Shared code in _fig4.py (calibration from the axis ticks; the curve by its colour). The green
legend line lies lower right, below the curve, so the topmost green run in a column is taken.
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
    return m.read_curve(image, at, m.GREEN, 0.25, 10.0, pick="top")
