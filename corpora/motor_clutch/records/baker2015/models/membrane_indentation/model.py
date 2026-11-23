# Membrane-indentation relation of the Methods (p. 8), as printed:
#   F = E t pi delta^3 (ro^2 - ri^2) / (2 (ro - ri)^4 (1 - nu))
# Ports: E in kPa, t and delta in um, ro and ri in mm, F in mN. Computed in SI, returned in mN.
import math


def run(inputs, settings):
    E = inputs["E"] * 1e3          # kPa -> Pa
    t = inputs["t"] * 1e-6         # um -> m
    d = inputs["delta"] * 1e-6     # um -> m
    ro = inputs["ro"] * 1e-3       # mm -> m
    ri = inputs["ri"] * 1e-3       # mm -> m
    nu = inputs["nu"]
    F = E * t * math.pi * d ** 3 * (ro ** 2 - ri ** 2) / (2 * (ro - ri) ** 4 * (1 - nu))
    return {"F": F * 1e3}          # N -> mN


def symbolic():
    import sympy as sp
    E, t, delta, ro, ri = sp.symbols("E t delta ro ri", positive=True)
    nu = sp.Symbol("nu")
    Es, ts, ds, ros, ris = E * 1000, t * sp.Rational(1, 10**6), delta * sp.Rational(1, 10**6), ro / 1000, ri / 1000
    F = Es * ts * sp.pi * ds ** 3 * (ros ** 2 - ris ** 2) / (2 * (ros - ris) ** 4 * (1 - nu))
    return {"F": F * 1000}
