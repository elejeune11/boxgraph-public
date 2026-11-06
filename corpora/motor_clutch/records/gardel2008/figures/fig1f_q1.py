"""Fig. 1 F (PDF p. 2): box plots of F-actin speed per cell region: the 25% (lower box bound).

Regions numbered 1 BG, 2 LP, 3 FA, 4 CB. Matched y labels: 30, 20, 10, 0 (30 at the topmost tick). See _box.py.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("gardel_box", Path(__file__).with_name("_box.py"))
B = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B)


def read(image, at):
    return B.read_stat(image, "q1", [(2, "LP"), (3, "FA"), (4, "CB")], 30.0, 10.0)
