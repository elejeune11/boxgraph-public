# Eq. 4 (p. 4): R ≈ 4 (Et It/(Em h eps0^2))^(1/3), with It = (pi/4)(ro^4 - ri^4) (SI footnote 6).
# Lengths in um, moduli in kPa, eps0 as a fraction; R in mm.
import math


def run(inputs, settings):
    It = math.pi / 4 * (inputs["ro"] ** 4 - inputs["ri"] ** 4)
    ratio = inputs["Et"] * It / (inputs["Em"] * inputs["h"] * inputs["e0"] ** 2)
    return {"R": 4 * ratio ** (1.0 / 3.0) * 1e-3}


def symbolic():
    import sympy as sp
    Et, ro, ri, Em, h, e0 = sp.symbols("Et ro ri Em h e0", positive=True)
    It = sp.pi / 4 * (ro**4 - ri**4)
    return {"R": 4 * (Et * It / (Em * h * e0**2)) ** sp.Rational(1, 3) / 1000}
