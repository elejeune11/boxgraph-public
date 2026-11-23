"""Supp. Fig. 8a: cell death (% EthD-1+), bars 1 = soft (light grey), 2 = stiff (dark grey) fibre
networks. y ticks 0-4. See _kit.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

FILLS = [((160, 159, 164), 25), ((50, 50, 50), 30)]
TICKS = [0, 1, 2, 3, 4]


def read(image, at):
    return K.bar_panel(image, FILLS, TICKS)
