"""Fig. 3b and 3d: two bars per panel, 1 = soft or 0.5 mg/ml (grey), 2 = stiff or 7.0 mg/ml (black).
The y tick values of each panel are given by its reading file. See _kit.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

FILLS = [((156, 154, 155), 30), ((35, 31, 32), 40)]


def read_panel(image, ticks):
    return K.bar_panel(image, FILLS, ticks)
