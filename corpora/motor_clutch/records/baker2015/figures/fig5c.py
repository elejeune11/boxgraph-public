"""Fig. 5c: cell area, bars 1-4 = hydrogel soft (grey), hydrogel stiff (black), fibres soft (grey),
fibres stiff (black). y ticks 0, 3,000, 6,000, 9,000. See _kit.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

FILLS = [((178, 178, 178), 30), ((35, 31, 32), 40)]
TICKS = [0, 3000, 6000, 9000]


def read(image, at):
    return K.bar_panel(image, FILLS, TICKS)
