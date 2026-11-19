# Eq. 1: lambda ~ (Et It/(Em h))^(1/3), with It ~ ro^4 - ri^4 (p. 3). Printed with "~": prefactor 1.
# Lengths in um, moduli in kPa (they cancel in the ratio); lambda in mm.


def run(inputs, settings):
    It = inputs["ro"] ** 4 - inputs["ri"] ** 4                    # um^4
    ratio = inputs["Et"] * It / (inputs["Em"] * inputs["h"])      # um^3
    return {"lam": ratio ** (1.0 / 3.0) * 1e-3}                   # um -> mm


def symbolic():
    import sympy as sp
    Et, ro, ri, Em, h = sp.symbols("Et ro ri Em h", positive=True)
    return {"lam": (Et * (ro**4 - ri**4) / (Em * h)) ** sp.Rational(1, 3) / 1000}
