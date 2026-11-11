import math

import numpy as np


def phi(x, n):
    """Eq. 5 with x = r/R."""
    return (n + 2.0) / n * (1.0 - x ** n)


def delta_eq3(n):
    # (1/S) int_S (phi^2 - 1) da with da = 2 pi r dr, S = pi R^2  ->  int_0^1 (phi^2 - 1) 2x dx
    xg, wg = np.polynomial.legendre.leggauss(200)
    x = 0.5 * (xg + 1.0)
    w = 0.5 * wg
    return float(np.sum(w * (phi(x, n) ** 2 - 1.0) * 2.0 * x))


def wall_integral_eq4(n):
    # oint dphi/dm dl around r = R: m is the outward normal, dl = R dtheta -> 2 pi R dphi/dr(R) = 2 pi dphi/dx(1)
    h = 1e-3
    f = [phi(1.0 - k * h, n) for k in range(5)]
    d = (25 * f[0] - 48 * f[1] + 36 * f[2] - 16 * f[3] + 3 * f[4]) / (12 * h)
    return 2.0 * math.pi * d


def run(inputs, settings):
    n = inputs["n"]
    return {"delta": delta_eq3(n), "Nint": wall_integral_eq4(n)}
