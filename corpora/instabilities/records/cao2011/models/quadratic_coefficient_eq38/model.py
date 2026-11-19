# Eq. 3.8 evaluated with the Biot modes (2.9)-(2.10), giving A of Eq. 4.2.
# Wavelength l = 1, k = 2 pi. For mode n:
#   u1 = f(nkx2) sin(nkx1), u2 = g(nkx2) cos(nkx1), lambda_1 q = nk h(nkx2) cos(nkx1).
# (1/2) d3Phi/dlambda dU^2 U^2 = (mu/lambda_1) Int {(lambda_1 Q)(r U1,1 - U2,2) + 2 r (U1,1 U2,2 - U1,2 U2,1)} dV
#                             = (mu l^2 A/lambda_W) n xi_n^2  (lambda_1 = lambda_W).
# The x1 average is taken on a uniform periodic grid (exact for these trigonometric products), the x2
# integral by adaptive quadrature over the decaying exponentials.
import math

import numpy as np
from scipy.integrate import quad


def modes(r):
    d = 1.0 - r * r
    a = 1.0 + r * r

    def f(z):
        return (-a * np.exp(r * z) + 2 * r * np.exp(z)) / d

    def fp(z):
        return (-a * r * np.exp(r * z) + 2 * r * np.exp(z)) / d

    def g(z):
        return (a * np.exp(r * z) - 2 * r * r * np.exp(z)) / d

    def gp(z):
        return (a * r * np.exp(r * z) - 2 * r * r * np.exp(z)) / d

    def h(z):
        return -a / r * np.exp(r * z)

    return f, fp, g, gp, h


def fields(r, n, x2, x1):
    """U1,1, U2,2, U1,2, U2,1 and lambda_1 Q of mode n (l = 1) at depth x2, over the x1 grid."""
    f, fp, g, gp, h = modes(r)
    k = 2 * math.pi
    s = n * k * x2
    c, si = np.cos(n * k * x1), np.sin(n * k * x1)
    return (n * k * f(s) * c, n * k * gp(s) * c, n * k * fp(s) * si, -n * k * g(s) * si, n * k * h(s) * c)


def grid(m):
    return (np.arange(m) + 0.5) / m


def coefficient_A(r, settings):
    x1 = grid(int(settings.get("n_x1", 64)))
    depth = float(settings.get("depth", 12.0))

    def integrand(x2):
        u11, u22, u12, u21, lq = fields(r, 1, x2, x1)
        return float(np.mean(lq * (r * u11 - u22) + 2 * r * (u11 * u22 - u12 * u21)))

    val = quad(integrand, -depth, 0.0, limit=400, epsabs=1e-13, epsrel=1e-12)[0]
    return val  # times mu l^2 / lambda_W, for n = 1 and xi_1 = 1


def run(inputs, settings):
    return {"A": coefficient_A(inputs["r"], settings)}
