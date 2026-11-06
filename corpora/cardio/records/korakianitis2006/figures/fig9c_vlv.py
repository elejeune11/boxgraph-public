"""Fig. 9(c) (PDF p. 12): V(lv)', the solid line with triangles: the second track at end-diastole, the bottom at end-systole, the top in late filling. See _kor.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kor", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kor.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)

# printed tick labels: y bottom to top, x left to right; the label at the axis corner (None: none)
Y = [40, 60, 80, 100, 120, 140]
X = [10, 10.5, 11]
CORNER = 20
# reader's choices: the legend region to ignore, and which track to take on each stretch of t
LEGEND = [1050, 0, 1900, 480]
ABOVE = None
RULES = [(10.0, 10.1, 1, None), (10.3, 10.3, -1, 4), (10.35, 10.4, -1, 3), (10.6, 10.65, 0, None), (10.75, 10.9, 0, None)]


def read(image, at):
    return _k.read_tracks(image, at, Y, X, CORNER, LEGEND, RULES, above=ABOVE)
