"""Fig. 18, t = 0.2 s (PDF p. 24): area A at t = 0.2 s without the longitudinal elasticity term, the continuous line (not at the two near-vertical jumps). See _s4.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_s4", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_s4.py"))
_s = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_s)

# printed tick labels (x, y) and the box corners they sit on; the reader's choices
CFG = dict(
    X=[5, 10],
    Xc={'lc': 0, 'rc': 15},
    Y=[0.8, 0.82, 0.84, 0.86, 0.88],
    Yc={'tc': 0.9, 'bc': 0.78},
    style='solid',
    legend=None,
    rules=[(-1000000000.0, 1000000000.0, 0, None)],
)


def read(image, at):
    return _s.read(image, at, CFG)
