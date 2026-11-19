"""Fig. 2(a) (PDF p. 2): e/e0 against t (minutes) for the representative embryo (red line).

Calibration by _fig2.py: x ticks every 10 min, labelled -20, 0, 20, 40 (the unlabelled ticks
between are -10, 10, 30; the box edges are -30 and 50 and carry no tick); y ticks labelled
0.2 to 1.2 in steps of 0.2, found mirrored on both sides.
"""
import importlib.util
from pathlib import Path


def _mod():
    spec = importlib.util.spec_from_file_location("hohn2015_fig2", Path(__file__).with_name("_fig2.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    return _mod().read_red(image, at, [-20, -10, 0, 10, 20, 30, 40], [0.2, 0.4, 0.6, 0.8, 1.0, 1.2])
