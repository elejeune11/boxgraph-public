def run(inputs, settings):
    return {"ratio": inputs["mu_f"] / inputs["mu_s"]}


def symbolic():
    import sympy as sp
    mu_f, mu_s = sp.symbols("mu_f mu_s", positive=True)
    return {"ratio": mu_f / mu_s}
