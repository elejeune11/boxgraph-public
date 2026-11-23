"""Elliptic integral Ie(ec), Supplementary Eq. (A13):
Ie = 4 / (3 pi ec^2) [ (1 + ec^2) Ke(ec) - Ee(ec) ],
with Ke, Ee the complete elliptic integrals of modulus ec (Eq. A9); scipy's ellipk/ellipe take
the parameter m = ec^2. At ec -> 0 the printed form is 0/0; its limit is taken from the series
Ke = pi/2 (1 + m/4 + ...), Ee = pi/2 (1 - m/4 - ...), which gives 1 + 7m/24."""
import math

from scipy.special import ellipe, ellipk


def run(inputs, settings):
    ec = inputs["ec"]
    m = ec * ec
    if m < 1e-6:
        return {"Ie": 1.0 + 7.0 * m / 24.0}
    return {"Ie": 4.0 / (3.0 * math.pi * m) * ((1 + m) * ellipk(m) - ellipe(m))}
