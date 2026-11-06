"""Fig. 14, bottom right (difference flow, t = 0.05 s) (PDF p. 20): the highest and the lowest point of the difference in flow rate. See _s4.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_s4", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_s4.py"))
_s = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_s)

# printed tick labels (x, y) and the box corners they sit on; the reader's choices
CFG = dict(
    X=[20, 40, 60, 80, 100, 120, 140],
    Xc={'lc': 0, 'rc': 160},
    Y=[-1, -0.5, 0, 0.5, 1],
    Yc={'tc': 1.5, 'bc': -1.5},
    style='extremes',
    legend=None,
)


def read(image, at):
    return _s.read(image, at, CFG)
