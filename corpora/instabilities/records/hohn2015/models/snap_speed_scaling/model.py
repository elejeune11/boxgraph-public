# U ~ E h^(5/2) / (mu R^(3/2)), printed without a prefactor: written with a prefactor of 1.
def run(inputs, settings):
    return {"U": inputs["E"] * inputs["h"] ** 2.5 / (inputs["mu"] * inputs["R"] ** 1.5)}


def symbolic():
    import sympy as sp
    E, h, mu, R = sp.symbols("E h mu R", positive=True)
    return {"U": E * h ** sp.Rational(5, 2) / (mu * R ** sp.Rational(3, 2))}
