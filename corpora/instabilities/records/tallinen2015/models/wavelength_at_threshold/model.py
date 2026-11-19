# The wavelength of linear instability as a function of the threshold growth g (blue curve,
# Fig. 2(b)): the modulus ratio eta whose first-unstable-mode threshold (Eq. 1 minimized over
# wavelength) equals g is found by Brent's method in [eta_lo, eta_hi] (g_c decreases with eta
# above eta_b); its wavelength l_c/a is converted to l/h with the printed h = a/gz, gz = 1/g.
import importlib.util
from pathlib import Path

from scipy.optimize import brentq

_spec = importlib.util.spec_from_file_location(
    "tallinen2015_first_unstable_mode", Path(__file__).resolve().parent.parent / "first_unstable_mode" / "model.py")
_fm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fm)


def mode_at(g, settings):
    """(l_c/a, eta) of the first unstable mode whose threshold is g."""
    def f(eta):
        return _fm.first_mode(eta, settings)[0] - g

    eta = brentq(f, settings.get("eta_lo", 0.53), settings.get("eta_hi", 20.0), xtol=1e-6)
    return _fm.first_mode(eta, settings)[1], eta


def run(inputs, settings):
    g = inputs["g"]
    la, _ = mode_at(g, settings)
    gz = 1.0 / g
    return {"l_over_h": la * gz}  # h = a/gz, so a/h = gz
