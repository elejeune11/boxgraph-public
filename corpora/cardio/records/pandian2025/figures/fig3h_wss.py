"""Fig. 3h (p. 6), "WSS in the networks": the black dashed central line of each control network (x = 1, 2, 3).
No whiskers. Log axis 10^1 ... 10^-3 dyn/cm2. See _cols.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_cols", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cols.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def read(image, at):
    cal = C.calibrate(image, (450, 2300, 60, 2800), [1, 0, -1, -2, -3], True)
    return C.read_column(image, at, cal, what="dashed central line")
