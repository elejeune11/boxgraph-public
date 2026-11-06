"""Fig. 17, bottom right (difference area, z to 10 cm) (PDF p. 23): area with minus area without the viscoelastic term (axis labels times 10^-3), the single line. See _s4.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_s4", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_s4.py"))
_s = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_s)

# printed tick labels (x, y) and the box corners they sit on; the reader's choices
CFG = dict(
    X=[1, 2, 3, 4, 5, 6, 7, 8, 9],
    Xc={'lc': 0, 'rc': 10},
    Y=[-0.001, 0, 0.001, 0.002, 0.003],
    Yc={'tc': 0.004, 'bc': -0.002},
    style='line',
    legend=None,
    rules=[(-1000000000.0, 1000000000.0, 0, 1)],
)


def read(image, at):
    return _s.read(image, at, CFG)
