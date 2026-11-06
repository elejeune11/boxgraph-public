"""Fig. 9(f) (PDF p. 12): V(ra)', the dotted line with triangles: the upper of the two atrial tracks. See _kor.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kor", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kor.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)

# printed tick labels: y bottom to top, x left to right; the label at the axis corner (None: none)
Y = [40, 60, 80, 100, 120]
X = [10, 10.5, 11]
CORNER = 20
# reader's choices: the legend region to ignore, and which track to take on each stretch of t
LEGEND = [1000, 0, 1900, 480]
ABOVE = None
RULES = [(9.85, 9.9, 2, 4), (10.05, 10.05, 2, 4), (10.1, 10.1, -2, 3), (10.2, 10.35, 0, 3), (10.5, 10.9, 2, 4)]


def read(image, at):
    return _k.read_tracks(image, at, Y, X, CORNER, LEGEND, RULES, above=ABOVE)
