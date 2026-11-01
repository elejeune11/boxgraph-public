"""Supplementary Fig. 2, the red mean with s.e.m. bar under 'Talin shRNA' (29 kPa). Method in _panels.py and _gen.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("elosegui2016_panels", Path(__file__).with_name("_panels.py"))
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)


def read(image, at):
    return _m.read(image, at, "figs2_shrna_29kpa")
