"""Fig. 2 (PDF p. 4): E(lv), the solid line (legend: E(lv)): the bottom track in diastole, the top one in systole. See _kor.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kor", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kor.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)

# printed tick labels: y bottom to top, x left to right; the label at the axis corner (None: none)
Y = [0, 1, 2, 3]
X = [10, 10.2, 10.4, 10.6, 10.8, 11]
CORNER = None
# reader's choices: the legend region to ignore, and which track to take on each stretch of t
LEGEND = [1900, 0, 2800, 420]
ABOVE = None
RULES = [(9.95, 10.0, -1, 2), (10.05, 10.4, 0, 2), (10.45, 11.0, -1, 2), (11.05, 11.05, 0, 2)]


def read(image, at):
    return _k.read_tracks(image, at, Y, X, CORNER, LEGEND, RULES, above=ABOVE)
