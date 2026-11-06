"""Fig. 5(e) (PDF p. 9): Q(ti), the solid line: the upper track in diastole, the 0 track in systole. See _kor.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kor", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kor.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)

# printed tick labels: y bottom to top, x left to right; the label at the axis corner (None: none)
Y = [-250, 0, 250, 500, 750, 1000, 1250]
X = [10, 10.5, 11]
CORNER = -500
# reader's choices: the legend region to ignore, and which track to take on each stretch of t
LEGEND = [1250, 0, 2450, 260]
ABOVE = None
RULES = [(9.85, 9.9, 0, 2), (10.0, 10.35, -1, None), (10.5, 10.9, 0, 2), (11.0, 11.15, -1, None)]


def read(image, at):
    return _k.read_tracks(image, at, Y, X, CORNER, LEGEND, RULES, above=ABOVE)
