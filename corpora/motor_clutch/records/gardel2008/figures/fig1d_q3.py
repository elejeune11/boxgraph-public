"""Fig. 1 D (PDF p. 2): box plots of traction stress per cell region: the 75% (upper box bound).

Regions numbered 1 BG, 2 LP, 3 FA, 4 CB. Matched y labels: 200, 150, 100, 50, 0 (200 at the topmost tick). See _box.py.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("gardel_box", Path(__file__).with_name("_box.py"))
B = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B)


def read(image, at):
    return B.read_stat(image, "q3", [(1, "BG"), (2, "LP"), (3, "FA"), (4, "CB")], 200.0, 50.0)
