# Eq. 2.8 (p. 5) read the other way: the nominal compressive strain eps = 1 - lambda at which the flat
# surface bifurcates for a given normalized wavenumber kbar (the strain of the bifurcation curve,
# figure 2a, at that kbar). kbar(eps) increases monotonically from 0 at eps = 0 to infinity at the root
# of lambda^3 + lambda^2 + lambda - 1 = 0, so the root is unique in that interval.
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("_kbar_eq28", os.path.join(_here, "..", "bifurcation_wavenumber_eq28", "model.py"))
_kb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kb)


def run(inputs, settings):
    from scipy.optimize import brentq

    target = inputs["kbar"]
    lam_b = brentq(lambda l: l**3 + l**2 + l - 1, 0.1, 0.99, xtol=1e-14)
    eps_hi = 1.0 - lam_b - 1e-12
    eps = brentq(lambda e: _kb.run({"eps": e}, {})["kbar"] - target, 1e-12, eps_hi, xtol=1e-12)
    return {"eps": eps}
