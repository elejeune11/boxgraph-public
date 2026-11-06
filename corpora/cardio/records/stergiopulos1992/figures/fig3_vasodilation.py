"""Fig. 3, dotted line: resting flow with vasodilation (abdominal stenosis). Each dot that stands clear
of the solid line is read at its centre (the first dots, near 63-70 %, merge with the solid line and
are not read); calibration in _fig3.py."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_fig3", Path(__file__).with_name("_fig3.py"))
f3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f3)


def read(image, at):
    return f3.read_dots(image)
