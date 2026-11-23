# The printed 1D formulas. All three stiffnesses in the same unit (pN/nm), as the printed Lc requires;
# L in um and phi in 1/um, so L/Lc is dimensionless; keff comes out in the stiffness unit.
import math


def run(inputs, settings):
    kp, ks, kc = inputs["kp"], inputs["ks"], inputs["kc"]
    Lc = (1.0 / inputs["phi"]) * math.sqrt((1.0 / kc) * 1.0 / (1.0 / ks + 1.0 / kp))
    x = inputs["L"] / Lc
    num = math.sqrt(kp * ks * kc) * (kp + ks) ** 1.5 * math.sinh(x)
    den = (kp**2 + ks**2) * math.cosh(x) + kp * ks * (2.0 + x * math.sinh(x))
    return {"keff": num / den}


def symbolic():
    import sympy as sp
    kp, ks, kc, L, phi = sp.symbols("kp ks kc L phi", positive=True)
    Lc = (1 / phi) * sp.sqrt((1 / kc) * 1 / (1 / ks + 1 / kp))
    x = L / Lc
    num = sp.sqrt(kp * ks * kc) * (kp + ks) ** sp.Rational(3, 2) * sp.sinh(x)
    den = (kp**2 + ks**2) * sp.cosh(x) + kp * ks * (2 + x * sp.sinh(x))
    return {"keff": num / den}
