"""Fig. 2c, collagen matrices panel: the 2 mg/ml series (blue circles)."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_fig2c", Path(__file__).with_name("_fig2c.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_series(image, at, (39, 69, 161), 40)
