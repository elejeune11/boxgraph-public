"""Fig. 6, dashed line: PI/PIn at the distal end of the posterior tibial artery (ankle). See _fig6.py."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_fig6", Path(__file__).with_name("_fig6.py"))
f6 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f6)


def read(image, at):
    return f6.read_line(image, at, "dashed")
