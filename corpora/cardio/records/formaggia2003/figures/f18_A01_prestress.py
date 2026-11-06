"""Fig. 18, t = 0.1 s (PDF p. 24): area A at t = 0.1 s with the longitudinal pre-stress term, the dotted line. See _s4.py for the method."""
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
    style='dots',
    legend=None,
    erode=0,
    dot=9,
    dotmin=2,
    speck=3,
    gap=50,
)


def read(image, at):
    return _s.read(image, at, CFG)
