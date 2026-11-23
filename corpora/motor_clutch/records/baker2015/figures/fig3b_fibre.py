"""Fig. 3b, middle panel (fibre networks): cell area, 1 soft, 2 stiff. y ticks 0-4,000."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_fig3", Path(__file__).with_name("_fig3.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_panel(image, [0, 1000, 2000, 3000, 4000])
