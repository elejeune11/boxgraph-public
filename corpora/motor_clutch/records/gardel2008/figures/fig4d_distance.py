"""Fig. 4 D left (PDF p. 5): distance from the cell edge of maximal (>95%) traction, mean
(square) and SD (error bar), for CONTROL (x = 1), BLEB (2), CA-RAC (3), CA-RHO (4), by colour.

x axis runs right to left: the long ticks carry the labels 10, 8, 6, 4, 2 (matched labels),
the frame edges 12 and 0 where they lie on the tick grid. See _hbars.py.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("gardel_hbars", Path(__file__).with_name("_hbars.py"))
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)


def read(image, at):
    return H.read_rows(image, 12.0, 0.0, 2.0)
