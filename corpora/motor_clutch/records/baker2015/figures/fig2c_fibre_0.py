"""Fig. 2c, fibre networks panel: the 0 mJ series (blue circles)."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_fig2c", Path(__file__).with_name("_fig2c.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_series(image, at, (39, 69, 161), 40)
