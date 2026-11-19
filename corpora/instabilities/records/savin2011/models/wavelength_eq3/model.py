# Eq. 3 (p. 4): lambda ≈ 36 (Et It/(Em h))^(1/3), with It = (pi/4)(ro^4 - ri^4) as defined in SI footnote 6.
# Lengths in um, moduli in kPa (they cancel); lambda in mm.
import math


def run(inputs, settings):
    It = math.pi / 4 * (inputs["ro"] ** 4 - inputs["ri"] ** 4)   # um^4
    ratio = inputs["Et"] * It / (inputs["Em"] * inputs["h"])       # um^3
    return {"lam": 36 * ratio ** (1.0 / 3.0) * 1e-3}


def symbolic():
    import sympy as sp
    Et, ro, ri, Em, h = sp.symbols("Et ro ri Em h", positive=True)
    It = sp.pi / 4 * (ro**4 - ri**4)
    return {"lam": 36 * (Et * It / (Em * h)) ** sp.Rational(1, 3) / 1000}
