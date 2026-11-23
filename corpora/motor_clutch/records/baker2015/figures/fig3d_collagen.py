"""Fig. 3d, bottom panel (collagen matrices): proliferation (% EdU+), 1 = 0.5 mg/ml, 2 = 7.0 mg/ml.
y ticks 0-15."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_fig3", Path(__file__).with_name("_fig3.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_panel(image, [0, 5, 10, 15])
