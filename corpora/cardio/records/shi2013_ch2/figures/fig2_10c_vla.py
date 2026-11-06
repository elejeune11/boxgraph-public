"""Fig. 2-10(c) (PDF p. 29): V(la)', the solid line with squares: the bottom track (its trough during atrial contraction, and with V(la) in diastasis). See _shi.py for the method."""
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
LEGEND = (10.4, 10.8, 110)
RULES = [(9.96, 10.08, -1, None), (10.52, 10.84, -1, None), (10.96, 11.08, -1, None)]

read = _s.reader(Y, X, CORNER, LEGEND, RULES)
