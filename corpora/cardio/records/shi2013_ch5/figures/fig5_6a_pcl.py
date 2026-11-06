"""Fig. 5-6(a) (p. 11): Pcl, the coarse dotted line, read where it is the highest ink of the plot
(above Pct and Ps, around its peak); see _common.py. Labels as in fig5_6a_pcu.py; the legend
(top right) is left out."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)

LEGEND = (1580, 60, 2300, 480)


def read(image, at):
    return _c.read_outermost(image, at, [-80, -40, 0, 40, 80, 120, 160], [36, 36.5, 37], -120, None,
                             top=True, legend_box=LEGEND)
