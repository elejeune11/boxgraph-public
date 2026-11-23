"""Supp. Fig. 3c: fluorescence intensity of soft networks (black bars) at the FITC-RGD concentrations
printed under them (0, 0.66, 2.0, 6.0 mM; returned as x, in that order). y ticks 0-10 by 2.
The legend's swatches do not stand on the x axis and are not taken for bars. See _kit.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

TICKS = [0, 2, 4, 6, 8, 10]
CONC = [0, 0.66, 2.0, 6.0]


def read(image, at):
    return K.bar_panel(image, [((0, 0, 0), 40)], TICKS, x_values=CONC)
