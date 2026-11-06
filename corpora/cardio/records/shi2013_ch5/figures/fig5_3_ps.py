"""Fig. 5-3 (p. 8): driving pressure in the air chamber, the single solid curve; see _common.py.
Printed labels: y -80 to 160 mmHg in steps of 40, with -120 at the corner; x 36, 37, 38 s, with 35
at the corner."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)


def read(image, at):
    return _c.read_single_curve(image, at, [-80, -40, 0, 40, 80, 120, 160], [36, 37, 38], -120, 35)
