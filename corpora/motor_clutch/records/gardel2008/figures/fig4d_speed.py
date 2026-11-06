"""Fig. 4 D right (PDF p. 5): F-actin speed at maximal (>95%) traction, mean (square) and
SD (error bar), for CONTROL (x = 1), BLEB (2), CA-RAC (3), CA-RHO (4), read by colour.

x axis: the frame edges carry the labels 0 and 35; the long ticks between them, 5 ... 30
(matched labels). See _hbars.py for how markers and bars are found.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("gardel_hbars", Path(__file__).with_name("_hbars.py"))
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)


def read(image, at):
    return H.read_rows(image, 0.0, 35.0, 5.0)
