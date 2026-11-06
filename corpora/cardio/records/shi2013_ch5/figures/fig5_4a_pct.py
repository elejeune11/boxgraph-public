"""Fig. 5-4(a) (p. 9): pressure at the tissue construct, the single solid curve; see _common.py.
Printed labels: y 0 to 120 mmHg in steps of 20 (the corner is below 0 and unlabelled); x 36, 37,
38 s, with 35 at the corner."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)


def read(image, at):
    return _c.read_single_curve(image, at, [0, 20, 40, 60, 80, 100, 120], [36, 37, 38], None, 35)
