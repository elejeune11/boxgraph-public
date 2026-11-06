"""Supplementary Fig. 2, the red discs over 0-1: single control + talin 1 head L325R cells on 29 kPa gels. Method in _panels.py and _gen.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("elosegui2016_panels", Path(__file__).with_name("_panels.py"))
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)


def read(image, at):
    return _m.read(image, at, "figs2_l325r_29kpa")
