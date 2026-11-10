"""Fig. 2H (p. 3): sphere proximity times, the band of overlapping blue dots traced as a line. See _fig2hi.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig2hi", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig2hi.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_fit(image, at, [0.015, 0.010, 0.005, 0.0], (20, 20, 240), 90)
