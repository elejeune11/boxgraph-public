def run(inputs, settings):
    return {"P": 2 * inputs["gamma"] / (inputs["R"] * 1e-4)}  # um -> cm


def symbolic():
    import sympy as sp
    gamma, R = sp.symbols("gamma R", positive=True)
    return {"P": 2 * gamma / (R * sp.Rational(1, 10**4))}
