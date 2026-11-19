# The cross section at the torque maximum: phi = a2 sin(2 mu) with a2 from Eq. 7 at kappa-bar_B of
# Eq. 9 (the paper notes this a2 is -1/3 for every pressure). Its shape x(mu) = int cos(mu' + phi),
# y(mu) = int sin(mu' + phi) (p. 2) is computed either with the first-order Taylor expansion in phi
# that the paper uses for Eqs. 6-8 (setting expansion: first_order) or exactly (expansion: exact).
# Outputs, both relative to the undeformed circle of radius R:
#   flattening = 1 - (y_max - y_min) / 2R          ("squeezed in the y direction")
#   moment_reduction = 1 - I / (pi R^3 t),  I = t R int (y - y_c)^2 dmu about the centroidal x axis
import math

import numpy as np


def _integrate(f, mu):
    n = len(f)
    c = np.fft.rfft(f)
    mean = c[0].real / n
    k = np.arange(len(c))
    g = np.zeros_like(c)
    g[1:] = c[1:] / (1j * k[1:])
    F = np.fft.irfft(g, n)
    return mean * mu + F - F[0]


def run(inputs, settings):
    pbar = inputs["pbar"]
    kbarB = math.sqrt(8 / 3 + 8 * pbar / 9)  # Eq. 9
    a2 = -kbarB**2 / (8 * (1 + pbar / 3))  # Eq. 7
    n = int(settings.get("n_grid", 4096))
    mu = 2 * np.pi * np.arange(n) / n
    phi = a2 * np.sin(2 * mu)
    if settings.get("expansion", "first_order") == "exact":
        y = _integrate(np.sin(mu + phi), mu)
    else:  # sin(mu + phi) ~ sin mu + phi cos mu
        y = _integrate(np.sin(mu) + phi * np.cos(mu), mu)
    flattening = 1 - (y.max() - y.min()) / 2
    w = 2 * np.pi / n
    yc = w * np.sum(y) / (2 * np.pi)
    second_moment = w * np.sum((y - yc) ** 2)
    return {"flattening": float(flattening), "moment_reduction": float(1 - second_moment / math.pi)}
