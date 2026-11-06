"""Fig. 12, panel A (PDF p. 18): area A, the single line. See _fig.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)

# printed tick labels (x, y); the reader's choices: the legend region to ignore and which track to take
CFG = dict(
    X=[0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8],
    Xc={'lc': 0, 'rc': 2},
    x_side="top",
    Y=[1.135, 1.14],
    Yc={'tc': 1.145, 'bc': 1.13},
    legend=None,
    rules=[(0, 2, 0, None)],
)


def read(image, at):
    return _f.read_tracks(image, at, CFG)
