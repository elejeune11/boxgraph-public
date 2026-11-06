"""Fig. 14, bottom left (flow rate, t = 0.05 s) (PDF p. 20): flow rate Q with the inertia term at t = 0.05 s, the single line. See _s4.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_s4", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_s4.py"))
_s = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_s)

# printed tick labels (x, y) and the box corners they sit on; the reader's choices
CFG = dict(
    X=[20, 40, 60, 80, 100, 120, 140],
    Xc={'lc': 0, 'rc': 160},
    Y=[-20, 0, 20],
    Yc={'tc': 40, 'bc': -40},
    style='line',
    legend=None,
    rules=[(-1000000000.0, 1000000000.0, 0, 1)],
)


def read(image, at):
    return _s.read(image, at, CFG)
