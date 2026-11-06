"""Fig. 6, panel A (PDF p. 15): area A, the dotted line (legend: alpha2 = 0; alpha3 = 3): the bottom track where the lines part (about 0.06-0.12 s); elsewhere all three lines coincide. See _fig.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)

# printed tick labels (x, y); the reader's choices: the legend region to ignore and which track to take
CFG = dict(
    X=[0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.16],
    Xc={'lc': 0, 'rc': 0.18},
    x_side="bottom",
    Y=[0.8, 0.85, 0.9],
    Yc={},
    legend=(1780, 40, 2270, 275),
    rules=[(0, 2, -1, None)],
)


def read(image, at):
    return _f.read_tracks(image, at, CFG)
