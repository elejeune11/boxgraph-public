"""Fig. 5-6(a) (p. 11): Pcu, the fine dotted line near 0 mmHg, read where it is the lowest ink of
the plot (while Ps, the dash-dot line, is above it); see _common.py. Printed labels: y -80 to 160
mmHg in steps of 40, with -120 at the corner; x 36, 36.5, 37 s (the corner is unlabelled). The
legend (top right) is left out."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)

LEGEND = (1580, 60, 2300, 480)  # crop pixels: the legend's sample lines and labels


def read(image, at):
    return _c.read_outermost(image, at, [-80, -40, 0, 40, 80, 120, 160], [36, 36.5, 37], -120, None,
                             top=False, legend_box=LEGEND)
