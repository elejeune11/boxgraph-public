"""Fig. 5(a) (PDF p. 9): P(la), the solid line: the bottom track (in diastole it coincides with P(lv)), second from the bottom where P(lv) dips below it. See _kor.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kor", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kor.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)

# printed tick labels: y bottom to top, x left to right; the label at the axis corner (None: none)
Y = [20, 40, 60, 80, 100, 120, 140, 160]
X = [10, 10.5, 11]
CORNER = 0
# reader's choices: the legend region to ignore, and which track to take on each stretch of t
LEGEND = [1300, 0, 2400, 370]
ABOVE = None
RULES = [(9.85, 10.4, -1, None), (10.45, 10.45, -2, 3), (10.5, 11.15, -1, None)]


def read(image, at):
    return _k.read_tracks(image, at, Y, X, CORNER, LEGEND, RULES, above=ABOVE)
