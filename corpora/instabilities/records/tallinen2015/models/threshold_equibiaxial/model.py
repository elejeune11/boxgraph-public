# Linear-instability threshold for transversely isotropic (equibiaxial) growth g = gx = gy (p. 4):
# the plane-strain results hold with eta -> gy eta and g -> gx sqrt(gy), so the threshold g solves
# g^(3/2) = g_c(g eta), g_c the first-unstable-mode threshold of Eq. 1. f(g) = g_c(g eta) - g^(3/2)
# is positive at g -> 1 and negative once g^(3/2) exceeds gb; the root is found by Brent's method
# in [g_lo, g_hi] (reader's choice).
import importlib.util
from pathlib import Path

from scipy.optimize import brentq

_spec = importlib.util.spec_from_file_location(
    "tallinen2015_first_unstable_mode", Path(__file__).resolve().parent.parent / "first_unstable_mode" / "model.py")
_fm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fm)


def run(inputs, settings):
    eta = inputs["eta"]

    def f(g):
        return _fm.first_mode(g * eta, settings)[0] - g ** 1.5

    g = brentq(f, settings.get("g_lo", 1.0001), settings.get("g_hi", 1.6), xtol=1e-7)
    return {"g": g}
