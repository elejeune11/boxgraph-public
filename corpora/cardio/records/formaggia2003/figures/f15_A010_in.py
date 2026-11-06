"""Fig. 15, area at t = 0.010 s (PDF p. 21): area A at t = 0.010 s, the continuous line (with inertia, wall density 1 g/cm^3). See _s4.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_s4", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_s4.py"))
_s = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_s)

# printed tick labels (x, y) and the box corners they sit on; the reader's choices
CFG = dict(
    X=[2, 4, 6, 8, 10, 12, 14, 16, 18],
    Xc={'lc': 0, 'rc': 20},
    Y=[0.8, 0.82, 0.84, 0.86],
    Yc={'tc': 0.88, 'bc': 0.78},
    style='solid',
    legend=[1659, 39, 2181, 228],
    rules=[(8.3, 9, -1, 2), (11, 11.6, -1, 2), (-1000000000.0, 1000000000.0, 'auto', None)],
)


def read(image, at):
    return _s.read(image, at, CFG)
