# Number of clutches: surface density times the surface of legend A's cylinder. The printed
# formula divides the density by (l d pi), which is not dimensionless (see questions).


def run(inputs, settings):
    return {"n": inputs["rho"] * inputs["A"]}


def symbolic():
    import sympy as sp
    rho, A = sp.symbols("rho A", positive=True)
    return {"n": rho * A}
