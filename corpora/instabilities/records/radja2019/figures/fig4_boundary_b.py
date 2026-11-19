# Fig. 4: the vertical boundary line just left of l0 = 4.5 (right edge of the purple and orange
# shaded regions). Searched between l0 = 4.2 and 4.49.
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig4", os.path.join(os.path.dirname(__file__), "_fig4.py"))
_fig4 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fig4)


def read(image, at):
    return _fig4.read_line(image, at, 4.2, 4.49)
