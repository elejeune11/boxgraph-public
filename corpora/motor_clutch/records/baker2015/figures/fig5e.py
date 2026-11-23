"""Fig. 5e: number of FAs, bars 1-4 = hydrogel soft (grey), hydrogel stiff (black), fibres soft (grey),
fibres stiff (black). y ticks 0, 100, 200, 300. See _kit.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

FILLS = [((178, 178, 178), 30), ((35, 31, 32), 40)]
TICKS = [0, 100, 200, 300]


def read(image, at):
    return K.bar_panel(image, FILLS, TICKS)
