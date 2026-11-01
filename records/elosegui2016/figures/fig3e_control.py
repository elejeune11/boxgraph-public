"""Fig. 3e, red filled discs with s.e.m. bars: control cells. Method in _fig3.py and _kit.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("elosegui2016_fig3", Path(__file__).with_name("_fig3.py"))
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)


def read(image, at):
    return _m.points(image, "e", "red")
