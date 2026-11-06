"""Fig. 4, the 90 % stenosis line (dash-dot): the lowest line. See _fig4.py."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_fig4", Path(__file__).with_name("_fig4.py"))
f4 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f4)


def read(image, at):
    return f4.read(image, at, 0)
