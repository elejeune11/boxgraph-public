def run(inputs, settings):
    return {"lam1": 1 - inputs["eps"]}


def symbolic():
    import sympy as sp
    eps = sp.symbols("eps", positive=True)
    return {"lam1": 1 - eps}
