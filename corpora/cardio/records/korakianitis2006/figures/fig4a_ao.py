"""Fig. 4(a) (PDF p. 8): Angle(ao), the dash-dot line: 75 deg where it is the upper track (aortic valve open), 0 where it is the lower or only track. See _kor.py for the method."""
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
RULES = [(10.95, 10.95, -1, 2), (11.05, 11.1, -1, 1), (11.15, 11.25, 0, 2), (11.35, 11.4, -1, 1), (11.45, 11.95, -1, 2), (12.05, 12.05, -1, 1)]


def read(image, at):
    return _k.read_tracks(image, at, Y, X, CORNER, LEGEND, RULES, above=ABOVE)
