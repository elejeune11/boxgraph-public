"""Fig. 2(a), the blue discs: talin 2 shRNA cells. Method in _panels.py and _gen.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("elosegui2016_panels", Path(__file__).with_name("_panels.py"))
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)


def read(image, at):
    return _m.read(image, at, "fig2a_shrna")
