"""Elliptic integral Ie(ec), Supplementary Eq. (A11), middle form:
Ie = (1/(3 pi)) int_0^{2 pi} (2 - (1 + ec^2) sin^2 phi) / (1 - ec^2 sin^2 phi)^{3/2} dphi."""
import math

from scipy.integrate import quad


def run(inputs, settings):
    e2 = inputs["ec"] ** 2
    f = lambda ph: (2 - (1 + e2) * math.sin(ph) ** 2) / (1 - e2 * math.sin(ph) ** 2) ** 1.5
    val, _ = quad(f, 0.0, 2 * math.pi, limit=200, epsabs=1e-13, epsrel=1e-12)
    return {"Ie": val / (3 * math.pi)}
