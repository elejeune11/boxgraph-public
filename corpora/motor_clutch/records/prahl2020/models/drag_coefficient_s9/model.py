# Pa s * mm / um^2: 12 mu[Pa s] L[1e-3 m] / (b[1e-6 m])^2 is in Pa s / m = N s m^-3;
# 1 N s m^-3 = 1e12 pN s / 1e18 um^3 = 1e-6 pN s um^-3.
def run(inputs, settings):
    si = 12.0 * inputs["mu"] * inputs["L"] * 1e-3 / (inputs["b"] * 1e-6) ** 2
    return {"dg": si * 1e-6}


def symbolic():
    import sympy as sp
    mu, L, b = sp.symbols("mu L b", positive=True)
    return {"dg": 12 * mu * L * sp.Rational(1, 1000) / (b * sp.Rational(1, 10**6)) ** 2 * sp.Rational(1, 10**6)}
