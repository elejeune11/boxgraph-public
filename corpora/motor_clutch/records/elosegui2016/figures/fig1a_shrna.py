"""Fig. 1(a), the blue inverted triangles with s.e.m. bars: talin 2 shRNA cells (the same data as Fig. 3d). Method in _panels.py and _gen.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("elosegui2016_panels", Path(__file__).with_name("_panels.py"))
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)


def read(image, at):
    return _m.read(image, at, "fig1a_shrna")
