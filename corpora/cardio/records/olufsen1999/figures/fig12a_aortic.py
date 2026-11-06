"""Fig. 12(A) (PDF p. 11): the thick solid line 'Aortic' (measured, ref. 41). See _fig12.py.

Labels matched: x ticks, left to right, after the first: 0, .1, .2, .3, .4, .5, .6, .7 (the first
tick, printed '-0.3', is left out of the fit; by the spacing of the others it sits at -0.03 s).
y ticks, bottom to top: 80, 90, 100, 110, 130 (the tick of the label 120 is not found in the scan).
The thick line is read on its upstroke, where it is the uppermost thick run (the other curves are
still at their foot), and from its fall after the peak through the incisura, where it is the lowest
(all other curves lie above it).
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig12", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig12.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    cal = _f.calibrate(image, [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7], slice(1, None),
                       [80.0, 90.0, 100.0, 110.0, 130.0], slice(None))
    up = [x for x in at if x < 0.1]
    down = [x for x in at if x >= 0.1]
    return _f.read_thick(cal, up, "uppermost", 80.0) + _f.read_thick(cal, down, "lowest", 80.0)
