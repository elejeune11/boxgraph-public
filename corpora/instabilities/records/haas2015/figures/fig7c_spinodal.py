"""Fig. 7(c) (PDF p. 7): the thick green curve bounding the unstable (cross-hatched) region, the
spinodal curve through the extrema of the branches, kR against d/R.

Calibration by _colour_curves.py: labelled y ticks 20, 10 from the top; 0.1 in d/R per x tick.
Green (0, 153, 0) is also the cross hatching and the word "unstable"; these are thinner than the
curve or span less than 0.3 in d/R, and `_fig7.thick` leaves them out. A column is read only
where it holds exactly one run (under the orange dot at the top the curve is hidden).
"""
import importlib.util
from pathlib import Path


def _h():
    spec = importlib.util.spec_from_file_location("haas2015_fig7", Path(__file__).with_name("_fig7.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    h = _h()
    cal = h.cc().calibrate(image, [20.0, 10.0], 0.1)
    curve, _ = h.thick(cal, h.plot_box(cal, h.colour(cal, (0, 153, 0))))
    return h.read_runs(cal, curve, at, lambda rs, col: rs[0] if len(rs) == 1 else None,
                       "thick green curve (unstable region) of Fig. 7(c)")
