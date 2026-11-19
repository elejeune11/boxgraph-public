# eta_s: the modulus ratio at which the first-unstable-mode threshold of Eq. 1 equals the
# sulcification threshold gs (p. 2). g_c(eta) decreases with eta above eta_b, so the crossing is
# bracketed in [eta_lo, eta_hi] (reader's choice) and found by Brent's method.
import importlib.util
from pathlib import Path

from scipy.optimize import brentq

_spec = importlib.util.spec_from_file_location(
    "tallinen2015_first_unstable_mode", Path(__file__).resolve().parent.parent / "first_unstable_mode" / "model.py")
_fm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fm)


def eta_s(gs, settings):
    def f(eta):
        return _fm.first_mode(eta, settings)[0] - gs

    return brentq(f, settings.get("eta_lo", 0.6), settings.get("eta_hi", 5.0), xtol=1e-7)


def run(inputs, settings):
    return {"eta_s": eta_s(inputs["gs"], settings)}
