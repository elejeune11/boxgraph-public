"""Fig. 3e (p. 6), "Radius of the networks": the black central line of each of the three control networks
(x = 1, 2, 3 for Network-1, -2, -3), with the grey whiskers (caps at the outermost dots). See _cols.py.
Linear y axis, labels 100 ... 0 um."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_cols", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cols.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def read(image, at):
    cal = C.calibrate(image, (400, 2450, 50, 2100), [100, 80, 60, 40, 20, 0], False)
    return C.read_column(image, at, cal, with_caps=True, capfrac=0.13)
