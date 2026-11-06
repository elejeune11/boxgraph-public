"""Fig. 7(a) (PDF p. 10): Ang(ao, normal), the solid line. See _kor.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kor", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kor.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)

# printed tick labels: y bottom to top, x left to right; the label at the axis corner (None: none)
Y = [0, 20, 40, 60, 80, 100]
X = [10, 10.5, 11]
CORNER = None
# reader's choices: the legend region to ignore, and which track to take on each stretch of t
LEGEND = None
ABOVE = 85
RULES = [(9.85, 9.9, -1, 2), (10.05, 10.05, -1, 1), (10.15, 10.3, 0, 2), (10.35, 10.4, -1, 1), (10.5, 10.9, -1, 2), (11.05, 11.05, -1, 1), (11.15, 11.15, 0, 2)]


def read(image, at):
    return _k.read_tracks(image, at, Y, X, CORNER, LEGEND, RULES, above=ABOVE)
