"""Fig. 1e: hydrogel Young's modulus (kPa), four black bars at the UV exposures printed under them
(1,000, 1,500, 3,000, 18,000 mJ cm-2; returned as x, in that order). y ticks 0, 20, 40, 60.
See _kit.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

FILLS = [((35, 31, 32), 40)]
TICKS = [0, 20, 40, 60]
DOSES = [1000, 1500, 3000, 18000]


def read(image, at):
    """All four bars, or only those at the doses in `at`."""
    out = K.bar_panel(image, FILLS, TICKS, x_values=DOSES)
    return [r for r in out if not at or any(abs(r["x"] - float(a)) < 1e-9 for a in at)]
