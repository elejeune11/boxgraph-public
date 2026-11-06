"""Fig. 3d, blue filled discs with s.e.m. bars: talin 2 shRNA cells (the data of Fig. 1a). Method in _fig3.py and _kit.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("elosegui2016_fig3", Path(__file__).with_name("_fig3.py"))
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)


def read(image, at):
    return _m.points(image, "d", "blue")
