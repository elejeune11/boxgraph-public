"""Fig. 2(d) (PDF p. 5): the solid red curve, linear WT model, actin flow v against E.

Read by the shared code in _fig.py. x: log axis, major ticks at the decades 10^2 (spine) to 10^6
left of the break, labelled 10^2, 10^4, 10^6 on every other one. y: labelled ticks 0, 40, 80, 120.
The solid line is the fully saturated red; the dotted talin WT curve is drawn lighter and falls
outside the colour box, and on the plateau it lies below the solid one (the top run is taken).
Read only up to 10^6 (right of the break both lines are drawn faded).
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("liu2025_fig", Path(__file__).with_name("_fig.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)

SPEC = {
    "x": {"scale": "log10", "region": (36, 172), "marks": [(0, 1e2), (2, 1e4), (4, 1e6)]},
    "y": {"marks": [(0, 0), (1, 40), (2, 80), (3, 120)]},
    "rgb": ((215, 0, 0), (255, 60, 60)),
    "pick": "top",
    "blank": [(140, 70, 250, 120), (40, 118, 65, 158)],  # the legend lines and markers (crop pixels: c0, r0, c1, r1)
}


def read(image, at):
    return F.read_curve(image, SPEC, at)


def debug(image):
    cal = F.calibrate(image, SPEC)
    return {"sp": cal["sp"], "xt": cal["xt"], "yt": cal["yt"]}
