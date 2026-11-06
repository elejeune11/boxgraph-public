"""Fig. 8, the three lines together beyond 58 %, where they meet and cross: the band they form.
See _fig8.py."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_fig8", Path(__file__).with_name("_fig8.py"))
f8 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f8)


def read(image, at):
    return f8.read_band(image, at)
