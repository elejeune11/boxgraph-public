"""Fig. 4g (p. 8), "WSS in the IL1beta networks": the black dashed central line of each IL-1beta network
(x = 1, 2, 3). No whiskers. Log axis 10^1 ... 10^-4 dyn/cm2. See _cols.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_cols", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cols.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def read(image, at):
    cal = C.calibrate(image, (400, 2000, 40, 2500), [1, 0, -1, -2, -3, -4], True)
    return C.read_column(image, at, cal, what="dashed central line")
