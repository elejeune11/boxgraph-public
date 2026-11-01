"""Supp. Fig. 3b, G' of the 3.4 kPa ionic gel: the filled red circles. See _figs3b.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_figs3b", Path(__file__).with_name("_figs3b.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_series(image, 'red')
