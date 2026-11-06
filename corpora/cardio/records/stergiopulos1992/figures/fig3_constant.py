"""Fig. 3, solid line: Q/Qn for constant distal resistance (abdominal stenosis). Traced from x = 1 %
along the lowest of the lines near Q/Qn = 1 (the dotted line lies on or above it); calibration in _fig3.py."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_fig3", Path(__file__).with_name("_fig3.py"))
f3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f3)


def read(image, at):
    return f3.read_curve(image, at, "solid")
