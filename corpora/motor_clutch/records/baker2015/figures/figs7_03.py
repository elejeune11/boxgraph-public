"""Supp. Fig. 7, 0.3 mg/ml panel: grey bins. x ticks 0.0-0.8, y ticks 0-30."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_hist", Path(__file__).with_name("_hist.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_hist(image, (212, 212, 212), [0, 10, 20, 30], [0.0, 0.2, 0.4, 0.6, 0.8])
