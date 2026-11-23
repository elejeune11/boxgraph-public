"""Fig. 2(d) (PDF p. 5): the solid green curve, linear KD model, actin flow v against E.

Read by the shared code in _fig.py; axes as in fig2d_linear_wt.py. The green line is the
saturated green; the data triangles are a lighter green outside the colour box. 10^11 is read at
the lone labelled tick right of the axis break.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("liu2025_fig", Path(__file__).with_name("_fig.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)

SPEC = {
    "x": {"scale": "log10", "region": (36, 172), "marks": [(0, 1e2), (2, 1e4), (4, 1e6)]},
    "y": {"marks": [(0, 0), (1, 40), (2, 80), (3, 120)]},
    "rgb": ((0, 170, 0), (90, 255, 90)),
    "pick": "top",
    "blank": [(140, 70, 250, 120), (40, 118, 65, 158)],  # the legend lines and markers (crop pixels: c0, r0, c1, r1)
}


def _col_1e11(cal, img):
    m = F.dark(img)
    runs = F._ticks_x(m, cal["sp"], (215, img.shape[1]))
    return max(F._majors(runs, 0.75))


def read(image, at):
    spec = dict(SPEC)
    spec["x_at_col"] = {1e11: lambda cal: _col_1e11(cal, image)}
    return F.read_curve(image, spec, at)
