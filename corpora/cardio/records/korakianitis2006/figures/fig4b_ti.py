"""Fig. 4(b) (PDF p. 8): Angle(ti), the solid line: upper track while the tricuspid valve is open, else the 0 track. See _kor.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kor", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kor.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)

# printed tick labels: y bottom to top, x left to right; the label at the axis corner (None: none)
Y = [0, 20, 40, 60, 80, 100]
X = [11, 11.2, 11.4, 11.6, 11.8, 12]
CORNER = None
# reader's choices: the legend region to ignore, and which track to take on each stretch of t
LEGEND = None
ABOVE = 85
RULES = [(10.95, 10.95, 0, 2), (11.1, 11.3, -1, 2), (11.35, 11.35, -1, 1), (11.4, 11.95, 0, 2)]


def read(image, at):
    return _k.read_tracks(image, at, Y, X, CORNER, LEGEND, RULES, above=ABOVE)
