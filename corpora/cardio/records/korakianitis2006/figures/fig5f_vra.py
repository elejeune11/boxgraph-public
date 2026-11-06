"""Fig. 5(f) (PDF p. 9): V(ra), the dotted line: the lower track except at end-systole. See _kor.py for the method."""
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
LEGEND = [880, 0, 1700, 240]
ABOVE = None
RULES = [(9.85, 9.9, -1, 2), (10.0, 10.15, -1, 2), (10.2, 10.35, 0, 2), (10.5, 10.9, -1, 2), (11.0, 11.15, -1, 2)]


def read(image, at):
    return _k.read_tracks(image, at, Y, X, CORNER, LEGEND, RULES, above=ABOVE)
