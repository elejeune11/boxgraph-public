"""Fig. 5 G (PDF p. 6): the red squares with error bars: v_w, the speed delineating the lower bound of the speed ranges, for BLEB (x = 2), RAC (3),
CONT (1), RHO (4), the long x ticks left to right.

Matched y labels: 25, 20, ..., 0 (25 at the topmost long tick; the 30 label sits on the top frame edge); short ticks halfway. See _vbars.py.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("gardel_vbars", Path(__file__).with_name("_vbars.py"))
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)

CONDITIONS = [(2, "BLEB"), (3, "RAC"), (1, "CONT"), (4, "RHO")]


def read(image, at):
    return V.read_panel(image, "red", CONDITIONS, 25.0, 5.0)
