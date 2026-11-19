"""Fig. 2(c) (PDF p. 2): most negative curvature kappa* in the bend region (1/um) against t
(minutes) for the representative embryo (red line).

Calibration by _fig2.py: x ticks every 10 min as in (a). y ticks every 0.02 1/um, labelled 0.0,
-0.04, ..., -0.16 at every second one; the label -0.2 is level with the bottom line of the box,
which is that mark. The ticks are taken from either side (one is lost on the left under the
embryo lines), from the bottom up.
"""
import importlib.util
from pathlib import Path


def _mod():
    spec = importlib.util.spec_from_file_location("hohn2015_fig2", Path(__file__).with_name("_fig2.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    ys = [0.0, -0.02, -0.04, -0.06, -0.08, -0.1, -0.12, -0.14, -0.16, -0.18]
    return _mod().read_red(image, at, [-20, -10, 0, 10, 20, 30, 40], ys, y_frame=(None, -0.2))
