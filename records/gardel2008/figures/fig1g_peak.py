"""Fig. 1 G right (PDF p. 2): histogram of F-actin speed in areas of highest (>95%) traction
stress, bar by bar.

Matched labels: x 0, 5, ..., 30 (long ticks; 0 and 30 at the frame edges); y 0 (bottom frame
edge), 100, 200, 300 on the long ticks, short ticks halfway (the top edge is not on the tick
grid and carries no label). See _hist.py.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("gardel_hist", Path(__file__).with_name("_hist.py"))
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)


def read(image, at):
    return H.read_hist(image, (0.0, 30.0), 5.0, (0.0, 400.0), 100.0)
