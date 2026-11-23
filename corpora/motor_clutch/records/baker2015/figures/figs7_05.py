"""Supp. Fig. 7, 0.5 mg/ml panel: grey bins. x ticks 0.5-3.0, y ticks 0-20."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_hist", Path(__file__).with_name("_hist.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_hist(image, (212, 212, 212), [0, 5, 10, 15, 20], [0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
