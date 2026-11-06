"""Fig. 5-5(a) (p. 10): displacement l of the silicon diaphragm, the single solid curve; see
_common.py. Printed labels: y -0.01 to 0.01 m in steps of 0.005, with -0.015 at the corner; x 36,
36.5, 37 s (the corner is before 36 and unlabelled)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)


def read(image, at):
    return _c.read_single_curve(image, at, [-0.01, -0.005, 0.0, 0.005, 0.01], [36, 36.5, 37], -0.015, None)
