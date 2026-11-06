# Average thickness = volume / area. V in ml (1 ml = 1e-6 m^3), S in m^2, W in um (1 m = 1e6 um).


def run(inputs, settings):
    return {"W": inputs["V"] * 1e-6 / inputs["S"] * 1e6}


def symbolic():
    import sympy as sp
    V, S = sp.symbols("V S", positive=True)
    return {"W": V * sp.Rational(1, 10**6) / S * 10**6}
