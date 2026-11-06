"""Fig. 5(a) (PDF p. 9): P(lv), the dotted line: with P(la) in filling, between the others in isovolumic phases, with P(ao) in ejection; steep stretches not read. See _kor.py for the method."""
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
RULES = [(9.85, 9.95, -1, 2), (10.0, 10.0, 1, 3), (10.2, 10.3, 0, 2), (10.45, 10.45, -1, 3), (10.5, 10.95, -1, 2), (11.0, 11.0, 1, 3)]


def read(image, at):
    return _k.read_tracks(image, at, Y, X, CORNER, LEGEND, RULES, above=ABOVE)
