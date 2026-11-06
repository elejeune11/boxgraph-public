"""Fig. 2-17(f) (PDF p. 40): V(ra)', the solid line with squares: the top track at end systole, the third track in diastole. See _shi.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_shi", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_shi.py"))
_s = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_s)

# printed tick labels: y bottom to top, x left to right; the label at the axis corner (None: none)
Y = [40, 60, 80, 100, 120, 140]
X = [10, 10.2, 10.4, 10.6, 10.8, 11]
CORNER = 20
# reader's choices: the legend region to ignore (x0, x1, y0: x0 <= x <= x1, y >= y0), and which
# track to take on each stretch of x: (x0, x1, rank from the top (negative: from the bottom), tracks expected)
LEGEND = (10.2, 10.6, 115)
RULES = [(10.2, 10.4, 0, None), (10.48, 10.96, 2, 4)]

read = _s.reader(Y, X, CORNER, LEGEND, RULES)
