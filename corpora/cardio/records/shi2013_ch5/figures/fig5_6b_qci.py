"""Fig. 5-6(b) (p. 11): Qci, the dashed line, read where it is the highest ink of the plot (its
positive lobe while the inlet valve is open); see _common.py. Printed labels: y -600 to 1000 ml/s
in steps of 200, with -800 at the corner; x 36, 36.5, 37 s (the corner is unlabelled). The legend
(top right) is left out."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)

LEGEND = (1990, 60, 2720, 600)


def read(image, at):
    return _c.read_outermost(image, at, [-600, -400, -200, 0, 200, 400, 600, 800, 1000], [36, 36.5, 37],
                             -800, None, top=True, legend_box=LEGEND)
