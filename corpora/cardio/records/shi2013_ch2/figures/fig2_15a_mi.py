"""Fig. 2-15(a) (PDF p. 37): Angle(mi), the solid line: the 75 degree track while the mitral valve is open, else the 0 track. See _shi.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_shi", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_shi.py"))
_s = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_s)

# printed tick labels: y bottom to top, x left to right; the label at the axis corner (None: none)
Y = [0, 20, 40, 60, 80, 100]
X = [11, 11.2, 11.4, 11.6, 11.8, 12]
CORNER = None
# reader's choices: the legend region to ignore (x0, x1, y0: x0 <= x <= x1, y >= y0), and which
# track to take on each stretch of x: (x0, x1, rank from the top (negative: from the bottom), tracks expected)
LEGEND = (11.6, 12.3, 85)
RULES = [(10.96, 10.96, 0, 2), (11.04, 11.12, 0, 1), (11.16, 11.28, -1, 2), (11.32, 11.4, 0, 1), (11.44, 11.96, 0, 2), (12.04, 12.08, 0, 1)]

read = _s.reader(Y, X, CORNER, LEGEND, RULES)
