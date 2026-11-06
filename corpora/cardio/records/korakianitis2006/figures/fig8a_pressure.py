"""Fig. 8(a) (PDF p. 11): Pressure effect, the dotted line: the lower track in systole, the single 0 track in diastole. See _kor.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kor", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kor.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)

# printed tick labels: y bottom to top, x left to right; the label at the axis corner (None: none)
Y = [-600000, -500000, -400000, -300000, -200000, -100000, 0, 100000, 200000]
X = [11, 11.5, 12]
CORNER = -700000
# reader's choices: the legend region to ignore, and which track to take on each stretch of t
LEGEND = None
ABOVE = 50000
RULES = [(10.95, 10.95, -1, 1), (11.15, 11.3, -1, 2), (11.45, 11.95, -1, 1)]


def read(image, at):
    return _k.read_tracks(image, at, Y, X, CORNER, LEGEND, RULES, above=ABOVE)
