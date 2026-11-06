"""Fig. 2(b): the proximal boundary condition (aortic inflow) over the second pulse, where no label
pointer touches it, as the topmost ink from its rise to its peak and fall to about 1.45 s. See _fig2.py."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_fig2", Path(__file__).with_name("_fig2.py"))
f2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f2)


def read(image, at):
    return f2.topmost(image, at, "b", -150.0, 590.0)
