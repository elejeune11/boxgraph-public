"""Fig. 6, solid line: PI/PIn just distal to the femoral stenosis. See _fig6.py."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_fig6", Path(__file__).with_name("_fig6.py"))
f6 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f6)


def read(image, at):
    return f6.read_line(image, at, "solid")
