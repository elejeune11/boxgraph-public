# Variant of m_point_eq211: the same fields and integrals, with the pressure term of Eq. 2.12b,
# -p(2) (u1,1(2)/lambda + lambda u2,2(2)), taken twice, as the second derivative of -p(J - 1) in the
# direction (u(2), p(2)) gives (see model.yaml, corrections).
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("_m_point_eq211", os.path.join(_here, "..", "m_point_eq211", "model.py"))
_mp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mp)


def run(inputs, settings):
    return _mp.m_point(settings, 2.0)
