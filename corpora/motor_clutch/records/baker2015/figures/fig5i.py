"""Fig. 5i: proliferation (% EdU+), bars 1-3 = soft (DMSO) grey, stiff (DMSO) black, soft (PF228) white
outlined. y ticks 0-25. See _kit.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

FILLS = [((178, 178, 178), 30), ((35, 31, 32), 40)]
TICKS = [0, 5, 10, 15, 20, 25]


def read(image, at):
    return K.bar_panel(image, FILLS, TICKS, outlined=True)
