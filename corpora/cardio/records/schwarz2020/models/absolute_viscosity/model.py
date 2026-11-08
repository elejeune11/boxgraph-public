def run(inputs, settings):
    return {"mu": inputs["mu_rel"] * inputs["mu_p"]}


def symbolic():
    import sympy as sp
    mu_rel, mu_p = sp.symbols("mu_rel mu_p", positive=True)
    return {"mu": mu_rel * mu_p}
