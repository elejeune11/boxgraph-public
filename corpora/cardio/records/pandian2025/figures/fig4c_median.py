"""Fig. 4c (p. 8): the black dashed central line of each group's bead velocities (x = 1 control, 2 IL-1beta).
Log axis 10^4 ... 10^0 um/s. See _fig4bc.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig4bc", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig4bc.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_median(image, at, "4c")
