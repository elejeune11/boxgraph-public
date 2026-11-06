"""Fig. 5-6(b) (p. 11): Qs, the dash-dot line, read where it is the lowest ink of the plot (its
negative lobe while the diaphragm moves down); see _common.py. Labels as in fig5_6b_qci.py; the
legend (top right) is left out."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)

LEGEND = (1990, 60, 2720, 600)


def read(image, at):
    return _c.read_outermost(image, at, [-600, -400, -200, 0, 200, 400, 600, 800, 1000], [36, 36.5, 37],
                             -800, None, top=False, legend_box=LEGEND)
