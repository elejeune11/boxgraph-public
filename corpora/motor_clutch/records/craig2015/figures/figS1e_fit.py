"""Supplemental figure 1(e) (PDF p. 20): the thick black model-fit curve (traction, Pa) drawn over the blue
measured points.

Read by the kit's read_curve (_kit.py) with a dark colour; the blue dots are far from black in RGB and are
not taken. Inner ticks only (the corner ticks merge with the frame); away from the tick columns x = 2, 4,
6, whose ticks are dark too.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("craig2015_kit", Path(__file__).with_name("_kit.py"))
_kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kit)


def read(image, at):
    return _kit.read_curve(image, at, [2, 4, 6], [80, 60, 40, 20], color=(0, 0, 0), tol=120, inner=True)
