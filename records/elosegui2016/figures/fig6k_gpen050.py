"""Fig. 6(k), the black discs: the highest GPen dose (legend '50 mM', 0.50 mM in the caption; q_fig6k_legend). Method in _panels.py and _gen.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("elosegui2016_panels", Path(__file__).with_name("_panels.py"))
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)


def read(image, at):
    return _m.read(image, at, "fig6k_gpen050")
