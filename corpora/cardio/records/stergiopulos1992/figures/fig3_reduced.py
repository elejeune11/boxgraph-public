"""Fig. 3, dashed line ("Elevated Flow"): Q/Qn with all distal resistances at 0.2 RT (abdominal
stenosis). Traced from x = 1 % near Q/Qn = 4, bridging the dash gaps; calibration in _fig3.py."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_fig3", Path(__file__).with_name("_fig3.py"))
f3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f3)


def read(image, at):
    return f3.read_curve(image, at, "dashed")
