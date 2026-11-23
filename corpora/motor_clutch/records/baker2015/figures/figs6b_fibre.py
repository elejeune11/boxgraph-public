"""Supp. Fig. 6b, right: bead displacement against distance on soft fibre networks (three cells).
See _s6b.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_s6b", Path(__file__).with_name("_s6b.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


def read(image, at):
    return S.read_panel(image, [0, 20, 40, 60], [0, 40, 80, 120])
