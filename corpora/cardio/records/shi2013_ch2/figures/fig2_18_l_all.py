"""Fig. 2-18 (PDF p. 42): L(all features), the solid line: the bottom track (with the dotted line where the two coincide). See _shi.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_shi", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_shi.py"))
_s = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_s)

# printed tick labels: y bottom to top, x left to right; the label at the axis corner (None: none)
Y = [-30, -20, -10, 0, 10]
X = [10, 10.2, 10.4, 10.6, 10.8, 11]
CORNER = None
# reader's choices: the legend region to ignore (x0, x1, y0: x0 <= x <= x1, y >= y0), and which
# track to take on each stretch of x: (x0, x1, rank from the top (negative: from the bottom), tracks expected)
LEGEND = (10.1, 11.12, 8)
RULES = [(9.94, 11.1, -1, None)]

read = _s.reader(Y, X, CORNER, LEGEND, RULES)
