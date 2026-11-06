"""Supplementary Fig. 1(b), the light blue bar under 'Talin 2 shRNA': talin 2 shRNA cells, α5β1 blocking antibody. Method in _panels.py and _gen.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("elosegui2016_panels", Path(__file__).with_name("_panels.py"))
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)


def read(image, at):
    return _m.read(image, at, "figs1b_shrna_ab")
