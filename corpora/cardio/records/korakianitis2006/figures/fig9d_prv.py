"""Fig. 9(d) (PDF p. 12): P(rv)', the dotted line with triangles: with P(po)' in ejection, the merged bottom track in diastole. See _kor.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kor", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kor.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)

# printed tick labels: y bottom to top, x left to right; the label at the axis corner (None: none)
Y = [5, 10, 15, 20, 25, 30]
X = [10, 10.5, 11]
CORNER = 0
# reader's choices: the legend region to ignore, and which track to take on each stretch of t
LEGEND = [1540, 0, 2450, 575]
ABOVE = None
RULES = [(10.2, 10.25, 1, 4), (10.5, 10.55, -1, 3), (10.65, 10.7, -1, 3), (10.75, 10.9, -1, 2)]


def read(image, at):
    return _k.read_tracks(image, at, Y, X, CORNER, LEGEND, RULES, above=ABOVE)
