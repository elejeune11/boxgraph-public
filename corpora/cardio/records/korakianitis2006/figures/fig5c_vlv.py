"""Fig. 5(c) (PDF p. 9): V(lv), the solid line: the upper track except at end-systole, where V(la) passes above it. See _kor.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kor", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kor.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)

# printed tick labels: y bottom to top, x left to right; the label at the axis corner (None: none)
Y = [40, 60, 80, 100, 120, 140]
X = [10, 10.5, 11]
CORNER = 20
# reader's choices: the legend region to ignore, and which track to take on each stretch of t
LEGEND = [900, 0, 1700, 240]
ABOVE = None
RULES = [(9.85, 9.9, 0, 2), (10.0, 10.1, 0, None), (10.2, 10.2, 0, 2), (10.3, 10.4, -1, 2), (10.5, 10.95, 0, None), (11.0, 11.1, 0, None)]


def read(image, at):
    return _k.read_tracks(image, at, Y, X, CORNER, LEGEND, RULES, above=ABOVE)
