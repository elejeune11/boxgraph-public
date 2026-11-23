"""Supp. Fig. 4: cell area on stiff fibre networks at the RGD concentrations printed under the bars
(0, 0.22, 0.66, 2.0, 6.0 mM; returned as x, in that order); grey bars with a dark outline, whose top
edge is the centre of the outline stroke. y ticks 0-6000 by 2000. See _kit.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

TICKS = [0, 2000, 4000, 6000]
CONC = [0, 0.22, 0.66, 2.0, 6.0]


def read(image, at):
    return K.bar_panel(image, [((128, 128, 128), 30)], TICKS, x_values=CONC, outline=True)
