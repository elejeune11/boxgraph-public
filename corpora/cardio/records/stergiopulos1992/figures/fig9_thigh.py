"""Fig. 9, solid line (upper thigh): bottom flat line up to 55 %, the top (rising) line from 65 %.
See _fig9.py."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_fig9", Path(__file__).with_name("_fig9.py"))
f9 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f9)


def read(image, at):
    return f9.read(image, at, "thigh")
