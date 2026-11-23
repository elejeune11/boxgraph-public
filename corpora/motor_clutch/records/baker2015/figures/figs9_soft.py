"""Supp. Fig. 9, left: diameters of soft (140 MPa) fibres, light blue bins. x ticks 0-4, y ticks 0-30."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_hist", Path(__file__).with_name("_hist.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_hist(image, (180, 180, 250), [0, 10, 20, 30], [0, 1, 2, 3, 4])
