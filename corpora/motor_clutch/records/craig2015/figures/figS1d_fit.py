"""Supplemental figure 1(d) (PDF p. 20): the thick black model-fit curve (actin flow speed, nm/s) drawn over
the cloud of blue measured points.

Read by the kit's read_curve (_kit.py) with a dark colour; the blue dots are far from black in RGB and are
not taken. Inner ticks only (the corner ticks merge with the frame); x ticks from the top side only (the
bottom ones sit among the dense dots and do not pair); read away from the tick columns x = 2, 4, 6, whose
ticks are dark too.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("craig2015_kit", Path(__file__).with_name("_kit.py"))
_kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kit)


_calibrate = _kit.calibrate


def _top_ticks(image, xlabels, ylabels, **kw):
    # the bottom x ticks sit among the dense dots and do not pair with the top ones: use the top ticks only
    return _calibrate(image, xlabels, ylabels, **{**kw, "x_top_only": True})


_kit.calibrate = _top_ticks  # this private copy of the kit only


def read(image, at):
    return _kit.read_curve(image, at, [2, 4, 6], [4, 2], color=(0, 0, 0), tol=120, inner=True)
