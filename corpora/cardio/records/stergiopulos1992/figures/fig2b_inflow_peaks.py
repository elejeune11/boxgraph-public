"""Fig. 2(b): the peak of the proximal boundary condition in each cycle (time and flow). See _fig2.py."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_fig2", Path(__file__).with_name("_fig2.py"))
f2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f2)


def read(image, at):
    return f2.peaks(image, "b", [(0.2, 0.45), (1.2, 1.45)], -150.0, 590.0)
