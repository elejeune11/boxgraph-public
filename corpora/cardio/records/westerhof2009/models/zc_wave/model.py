def run(inputs, settings):
    return {"Zc": inputs["PWV"] * inputs["rho"] / inputs["A"]}


def symbolic():
    import sympy as sp
    PWV, rho, A = sp.symbols("PWV rho A", positive=True)
    return {"Zc": PWV * rho / A}
