"""Fig. 13(c) (PDF p. 16): V(lv)', the solid line with triangles: the upper ventricular track (one track with V(lv) at end-systole). See _kor.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kor", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kor.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)

# printed tick labels: y bottom to top, x left to right; the label at the axis corner (None: none)
Y = [40, 60, 80, 100, 120, 140, 160]
X = [10, 10.5, 11]
CORNER = None
# reader's choices: the legend region to ignore, and which track to take on each stretch of t
LEGEND = [1050, 0, 1900, 520]
ABOVE = None
RULES = [(9.85, 9.9, 0, 4), (10.0, 10.05, 0, None), (10.25, 10.4, -1, 3), (10.5, 10.9, 0, 4), (11.0, 11.05, 0, None)]


def read(image, at):
    return _k.read_tracks(image, at, Y, X, CORNER, LEGEND, RULES, above=ABOVE)
