"""Fig. 5 F (PDF p. 6): the blue squares with error bars: sigma_s, the mean traction stress at v_s, for BLEB (x = 2), RAC (3),
CONT (1), RHO (4), the long x ticks left to right.

Matched y labels: 140, 120, ..., 0 (140 under the topmost long tick); short ticks halfway. See _vbars.py.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("gardel_vbars", Path(__file__).with_name("_vbars.py"))
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)

CONDITIONS = [(2, "BLEB"), (3, "RAC"), (1, "CONT"), (4, "RHO")]


def read(image, at):
    return V.read_panel(image, "blue", CONDITIONS, 140.0, 20.0)
