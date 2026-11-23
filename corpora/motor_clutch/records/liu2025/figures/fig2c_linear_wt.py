"""Fig. 2(c) (PDF p. 5): the solid red curve, linear WT model, cell traction P against E.

Read by the shared code in _fig.py; axes as in fig2c_linear_kd.py. The solid line is the fully
saturated red; the dotted talin WT curve beside it is drawn lighter (pink) and falls outside the
colour box, and lies below the solid one where both are present (so the top run is taken).
Right of the axis break both are drawn faded, so this curve is read only up to 10^6.
Near E = 3-5 x 10^3 the green KD line is drawn over the solid red one, and the only red run left
in a column is the dotted curve's (at 4 x 10^3 it read below the green line); no position there is read.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("liu2025_fig", Path(__file__).with_name("_fig.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)

SPEC = {
    "x": {"scale": "log10", "region": (14, 148), "marks": [(0, 1e2), (2, 1e4), (4, 1e6)]},
    "y": {"marks": [(0, 0), (1, 60), (2, 120), (3, 180)]},
    "rgb": ((215, 0, 0), (255, 60, 60)),
    "pick": "top",
    "blank": [(20, 0, 70, 50), (115, 60, 220, 125)],  # the two legends (crop pixels: c0, r0, c1, r1)
}


def read(image, at):
    return F.read_curve(image, SPEC, at)
