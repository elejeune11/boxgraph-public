# Eq. S9: kc = 4/7 * pi R E / ((1 + nu)(1 - 0.86 nu)).
# Ports: R um, E kPa, nu 1 -> k pN/nm; coef = k / (R E), dimensionless.
# um * kPa = 1e-6 m * 1e3 N/m^2 = 1e-3 N/m = 1 pN/nm.
import math


def run(inputs, settings):
    R, E, nu = inputs["R"], inputs["E"], inputs["nu"]
    coef = 4.0 / 7.0 * math.pi / ((1 + nu) * (1 - 0.86 * nu))
    return {"k": coef * R * E, "coef": coef}


def symbolic():
    import sympy as sp
    R, E, nu = sp.symbols("R E nu", positive=True)
    coef = sp.Rational(4, 7) * sp.pi / ((1 + nu) * (1 - sp.Rational(86, 100) * nu))
    return {"k": coef * R * E, "coef": coef}
