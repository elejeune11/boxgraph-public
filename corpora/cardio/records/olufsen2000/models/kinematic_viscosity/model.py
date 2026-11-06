def run(inputs, settings):
    return {"nu": inputs["mu"] / inputs["rho"]}


def symbolic():
    import sympy as sp
    mu, rho = sp.symbols("mu rho", positive=True)
    return {"nu": mu / rho}
