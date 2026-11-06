"""Fig. 13(a) (PDF p. 16): P(ao)', the dash-dot line with triangles: the lower of the two aortic tracks. See _kor.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kor", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kor.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)

# printed tick labels: y bottom to top, x left to right; the label at the axis corner (None: none)
Y = [20, 40, 60, 80, 100, 120, 140]
X = [10, 10.5, 11]
CORNER = 0
# reader's choices: the legend region to ignore, and which track to take on each stretch of t
LEGEND = [[1600, 0, 2100, 462], [2100, 0, 2600, 560]]
ABOVE = None
RULES = [(9.85, 10.05, 1, None), (10.25, 10.25, 1, 3), (10.4, 10.55, 1, None), (10.6, 10.85, -2, None), (10.9, 11.05, 1, None)]


def read(image, at):
    return _k.read_tracks(image, at, Y, X, CORNER, LEGEND, RULES, above=ABOVE)
