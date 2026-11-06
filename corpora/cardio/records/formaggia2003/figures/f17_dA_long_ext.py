"""Fig. 17, bottom left (difference area, z to 120 cm) (PDF p. 23): the highest and the lowest point of the difference in area. See _s4.py for the method."""
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
    style='extremes',
    legend=None,
)


def read(image, at):
    return _s.read(image, at, CFG)
