"""Fig. 5-4(b) (p. 10): flow-rate at the tissue construct, the single solid curve; see _common.py.
Printed labels: y 0 to 500 ml/s in steps of 100, with -100 at the corner; x 36, 37, 38 s, with 35
at the corner."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)


def read(image, at):
    return _c.read_single_curve(image, at, [0, 100, 200, 300, 400, 500], [36, 37, 38], -100, 35)
