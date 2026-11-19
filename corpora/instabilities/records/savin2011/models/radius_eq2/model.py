# Eq. 2: R ~ (Et It/(Em h eps0^2))^(1/3), It ~ ro^4 - ri^4 (p. 3). Printed with "~": prefactor 1.
# Lengths in um, moduli in kPa, eps0 as a fraction; R in mm.


def run(inputs, settings):
    It = inputs["ro"] ** 4 - inputs["ri"] ** 4
    ratio = inputs["Et"] * It / (inputs["Em"] * inputs["h"] * inputs["e0"] ** 2)
    return {"R": ratio ** (1.0 / 3.0) * 1e-3}


def symbolic():
    import sympy as sp
    Et, ro, ri, Em, h, e0 = sp.symbols("Et ro ri Em h e0", positive=True)
    return {"R": (Et * (ro**4 - ri**4) / (Em * h * e0**2)) ** sp.Rational(1, 3) / 1000}
