# Eq. 21 solved for gamma in (0, 1] (gamma = (r_d2/r_d1)^2 with r_d2 <= r_d1).
# eta(gamma) increases monotonically on (0, 1] for 2 < xi <= 3, so the root is unique.
from scipy.optimize import brentq


def _eta(gamma, xi):
    return (1 + gamma) / (1 + gamma ** (xi / 2)) ** (2 / xi)


def run(inputs, settings):
    xi, eta = inputs["xi"], inputs["eta"]
    return {"gamma": brentq(lambda g: _eta(g, xi) - eta, 1e-9, 1.0, xtol=1e-14)}
