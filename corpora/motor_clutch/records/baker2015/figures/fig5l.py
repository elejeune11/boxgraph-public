"""Fig. 5l: proliferation (% EdU+), bars 1-3 = soft grey, stiff black, soft-weld white outlined.
y ticks 0-40. See _kit.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

FILLS = [((178, 178, 178), 30), ((35, 31, 32), 40)]
TICKS = [0, 10, 20, 30, 40]


def read(image, at):
    return K.bar_panel(image, FILLS, TICKS, outlined=True)
