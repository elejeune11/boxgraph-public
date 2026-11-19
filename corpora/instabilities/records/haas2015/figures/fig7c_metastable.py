"""Fig. 7(c) (PDF p. 7): the thick blue curve bounding the metastable (hatched) band below the
critical point, kR against d/R.

Calibration by _colour_curves.py: labelled y ticks 20, 10 from the top; 0.1 in d/R per x tick.
Blue (0, 0, 255) is also the hatching, the two arrows and the word "metastable"; these are thinner
than the curve or span less than 0.3 in d/R, and `_fig7.thick` leaves them out. A column is read
only where it holds exactly one run.
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
    curve, _ = h.thick(cal, h.plot_box(cal, h.colour(cal, (0, 0, 255))))
    return h.read_runs(cal, curve, at, lambda rs, col: rs[0] if len(rs) == 1 else None,
                       "thick blue curve (metastable band) of Fig. 7(c)")
