"""Fig. 6a, the solid red line: model prediction with talin unfolding. Method in _fig6.py and _kit.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("elosegui2016_fig6", Path(__file__).with_name("_fig6.py"))
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)


def read(image, at):
    return _m.line(image, at, "a", "talin")
