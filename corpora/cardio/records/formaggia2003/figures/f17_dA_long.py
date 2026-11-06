"""Fig. 17, bottom left (difference area, z to 120 cm) (PDF p. 23): area with minus area without the viscoelastic term (axis labels times 10^-4), the single line. See _s4.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_s4", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_s4.py"))
_s = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_s)

# printed tick labels (x, y) and the box corners they sit on; the reader's choices
CFG = dict(
    X=[20, 40, 60, 80, 100],
    Xc={'lc': 0, 'rc': 120},
    Y=[-0.0004, -0.0002, 0, 0.0002, 0.0004],
    Yc={},
    style='line',
    legend=None,
    rules=[(-1000000000.0, 1000000000.0, 0, 1)],
)


def read(image, at):
    return _s.read(image, at, CFG)
