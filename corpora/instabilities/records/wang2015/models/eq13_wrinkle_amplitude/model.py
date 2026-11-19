# Eq. 13 as printed, with lengths in units of lambda^C_wrinkle and lambda_wrinkle = s (Eq. 9).
# Substituting u = x / s, the arc length of y = a sin(2 pi x / s) over one wavelength is
#   s * integral_0^1 sqrt(1 + (2 pi a / s)^2 cos^2(2 pi u)) du,
# and Eq. 13 sets it equal to 1. Solved for a = A_wrinkle / lambda^C_wrinkle.
import math

from scipy.integrate import quad
from scipy.optimize import brentq


def _arc(a, s):
    k = 2.0 * math.pi * a / s
    val, _ = quad(lambda u: math.sqrt(1.0 + (k * math.cos(2.0 * math.pi * u)) ** 2), 0.0, 1.0,
                  epsabs=1e-13, epsrel=1e-12, limit=200)
    return s * val


def run(inputs, settings):
    s = inputs["s"]
    if s >= 1.0:
        return {"A": 0.0}  # no compression beyond wrinkle initiation: flat
    a = brentq(lambda a: _arc(a, s) - 1.0, 0.0, 1.0, xtol=1e-14)
    return {"A": a}
