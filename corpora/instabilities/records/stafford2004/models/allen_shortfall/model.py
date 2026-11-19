"""Reconstructed: 100 (1 - Ef(Allen)/Ef(Eq. 2)) in percent, for the same d, h and Es.

Ef(Allen) = 12 Es / ((3 - nu_s)(1 + nu_s)) (d/2 pi h)^3   (plane-stress face on a half-space core)
Ef(Eq. 2) = 3 Es (1 - nu_f^2) / (1 - nu_s^2) (d/2 pi h)^3
"""


def run(inputs, settings):
    nu_f, nu_s = inputs["nu_f"], inputs["nu_s"]
    ratio = 4 * (1 - nu_s) / ((3 - nu_s) * (1 - nu_f**2))
    return {"shortfall": 100 * (1 - ratio)}


def symbolic():
    import sympy as sp

    nu_f, nu_s = sp.symbols("nu_f nu_s", positive=True)
    return {"shortfall": 100 * (1 - 4 * (1 - nu_s) / ((3 - nu_s) * (1 - nu_f**2)))}
