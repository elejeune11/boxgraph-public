"""Fig. 5h: pFAK at FAs (a.u.), bars 1-2 = soft (grey), stiff (black) fibre networks.
y ticks 0.00-0.05. See _kit.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

FILLS = [((178, 178, 178), 30), ((35, 31, 32), 40)]
TICKS = [0.0, 0.01, 0.02, 0.03, 0.04, 0.05]


def read(image, at):
    return K.bar_panel(image, FILLS, TICKS)
