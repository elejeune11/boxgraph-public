"""Fig. 2-6 (PDF p. 12): E(la), the dotted line: the lower track in systole, the upper one in diastole. See _shi.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_shi", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_shi.py"))
_s = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_s)

# printed tick labels: y bottom to top, x left to right; the label at the axis corner (None: none)
Y = [0, 1, 2, 3]
X = [10, 10.2, 10.4, 10.6, 10.8, 11]
CORNER = None
# reader's choices: the legend region to ignore (x0, x1, y0: x0 <= x <= x1, y >= y0), and which
# track to take on each stretch of x: (x0, x1, rank from the top (negative: from the bottom), tracks expected)
LEGEND = (10.62, 11.12, 2.3)
RULES = [(9.96, 10.0, 0, 2), (10.08, 10.44, -1, 2), (10.48, 10.88, 0, 2), (10.9, 10.98, 0, None)]

read = _s.reader(Y, X, CORNER, LEGEND, RULES)
