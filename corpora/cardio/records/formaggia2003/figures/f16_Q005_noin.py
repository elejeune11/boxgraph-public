"""Fig. 16, flow rate at t = 0.005 s (PDF p. 22): flow rate Q at t = 0.005 s, the dotted line (without inertia). See _s4.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_s4", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_s4.py"))
_s = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_s)

# printed tick labels (x, y) and the box corners they sit on; the reader's choices
CFG = dict(
    X=[2, 4, 6, 8, 10, 12, 14, 16, 18],
    Xc={'lc': 0, 'rc': 20},
    Y=[-20, 0, 20],
    Yc={'tc': 40, 'bc': -40},
    style='dots',
    legend=None,
    dot_rules=[(7.2, 8.3, -1, 2), (14, 20, -1, 2)],
)


def read(image, at):
    return _s.read(image, at, CFG)
