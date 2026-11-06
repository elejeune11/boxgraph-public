"""Fig. 2-21 (PDF p. 46): P(la)' with P(la), which coincide after the mitral valve closes: the bottom track. See _shi.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_shi", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_shi.py"))
_s = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_s)

# printed tick labels: y bottom to top, x left to right; the label at the axis corner (None: none)
Y = [10, 15, 20]
X = [9.95, 10, 10.05, 10.1]
CORNER = 5
# reader's choices: the legend region to ignore (x0, x1, y0: x0 <= x <= x1, y >= y0), and which
# track to take on each stretch of x: (x0, x1, rank from the top (negative: from the bottom), tracks expected)
LEGEND = (10.05, 10.12, 14)
RULES = [(10.04, 10.1, -1, None)]

read = _s.reader(Y, X, CORNER, LEGEND, RULES)
