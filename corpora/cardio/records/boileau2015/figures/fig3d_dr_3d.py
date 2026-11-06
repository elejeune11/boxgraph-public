"""Fig. 3(d) (PDF p. 10): the red curve (3D model of [33]), change in radius from diastole, carotid midpoint. See _wave.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_wave", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_wave.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)

# printed tick labels: x left to right, y bottom to top; whether the frame lines carry the end labels
X = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
XFRAME = (True, False)
Y = [0.0, 0.05, 0.1, 0.15, 0.2]
YFRAME = (True, True)
# reader's choice: the legend box to ignore (crop px), None if the panel has none
LEGEND = None


def read(image, at):
    return _k.read_red(image, at, X, Y, XFRAME, YFRAME, LEGEND)
