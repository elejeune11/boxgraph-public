def run(inputs, settings):
    # printed as a scaling: prefactor 1
    return {"P": inputs["lam"] * inputs["delta"] / (inputs["R"] * 1e-6)}


def symbolic():
    import sympy as sp
    lam, d, R = sp.symbols("lam delta R", positive=True)
    return {"P": lam * d / (R * sp.Rational(1, 10 ** 6))}
