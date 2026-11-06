"""Fig. 12(B) (PDF p. 11): the thick solid line '0 cm withdrawal' (measured, ref. 41). See _fig12.py.

Labels matched: x ticks, left to right: 0, .1, .2, .3, .4, .5, .6, .7. y ticks, bottom to top,
every second one: 80, 100, 120, 140 (the printed labels; the ticks between are unlabelled).
The thick line is read on its upstroke, where it is the uppermost thick run (the other curves are
still at their foot), and on its flat top near 122 mmHg, where it is the lowest (all other curves
peak above it).
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig12", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig12.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    cal = _f.calibrate(image, [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7], slice(None),
                       [80.0, 100.0, 120.0, 140.0], slice(0, None, 2))
    up = [x for x in at if x < 0.1]
    top = [x for x in at if x >= 0.1]
    return _f.read_thick(cal, up, "uppermost", 80.0) + _f.read_thick(cal, top, "lowest", 80.0)
