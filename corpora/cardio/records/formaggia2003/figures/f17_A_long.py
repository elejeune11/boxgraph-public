"""Fig. 17, top left (area, t = 0.2 s, z to 120 cm) (PDF p. 23): area A without the viscoelastic term at t = 0.2 s (the long pulse, period 0.3 s, as the z range suggests), the single line. See _s4.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_s4", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_s4.py"))
_s = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_s)

# printed tick labels (x, y) and the box corners they sit on; the reader's choices
CFG = dict(
    X=[20, 40, 60, 80, 100],
    Xc={'lc': 0, 'rc': 120},
    Y=[0.8, 0.85],
    Yc={'tc': 0.9},
    style='line',
    legend=None,
    y_side='right',
    rules=[(-1000000000.0, 1000000000.0, 0, 1)],
)


def read(image, at):
    return _s.read(image, at, CFG)
