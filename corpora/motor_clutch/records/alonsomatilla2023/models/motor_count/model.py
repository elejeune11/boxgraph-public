# Number of motors: surface density times surface.


def run(inputs, settings):
    return {"n": inputs["rho"] * inputs["A"]}


def symbolic():
    import sympy as sp
    rho, A = sp.symbols("rho A", positive=True)
    return {"n": rho * A}
