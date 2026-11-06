"""Fig. 8(b) (PDF p. 11): Pressure effect, the dotted line: the upper track in mid-diastole (with the velocity effect where they meet). See _kor.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kor", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kor.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)

# printed tick labels: y bottom to top, x left to right; the label at the axis corner (None: none)
Y = [-2000, -1000, 0, 1000, 2000, 3000, 4000, 5000]
X = [11, 11.5, 12]
CORNER = -3000
# reader's choices: the legend region to ignore, and which track to take on each stretch of t
LEGEND = None
ABOVE = 4000
RULES = [(11.05, 11.4, -1, 1), (11.55, 11.55, 0, 3), (11.6, 11.8, 0, 2), (11.85, 11.9, 0, 1)]


def read(image, at):
    return _k.read_tracks(image, at, Y, X, CORNER, LEGEND, RULES, above=ABOVE)
