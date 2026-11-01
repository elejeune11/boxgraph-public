"""Fig. 1 G left (PDF p. 2): histogram of F-actin speed over the entire cell front, bar by bar.

Matched labels: x 0, 5, ..., 30 (long ticks; 0 and 30 at the frame edges); y 0, 2000, 4000,
6000 on the long ticks and frame edges (0 bottom, 6000 top), short ticks halfway. See _hist.py.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("gardel_hist", Path(__file__).with_name("_hist.py"))
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)


def read(image, at):
    return H.read_hist(image, (0.0, 30.0), 5.0, (0.0, 6000.0), 2000.0)
