"""Fig. 2-10(b) (PDF p. 29): Q(mi)' with Q(mi) (triangles on Q(mi)'): the upper track in the late E-wave decay, where the two coincide. See _shi.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_shi", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_shi.py"))
_s = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_s)

# printed tick labels: y bottom to top, x left to right; the label at the axis corner (None: none)
Y = [200, 400, 600, 800, 1000, 1200]
X = [10, 10.2, 10.4, 10.6, 10.8, 11]
CORNER = None
# reader's choices: the legend region to ignore (x0, x1, y0: x0 <= x <= x1, y >= y0), and which
# track to take on each stretch of x: (x0, x1, rank from the top (negative: from the bottom), tracks expected)
LEGEND = (10.7, 11.12, 750)
RULES = [(10.54, 10.68, 0, 2)]

read = _s.reader(Y, X, CORNER, LEGEND, RULES)
