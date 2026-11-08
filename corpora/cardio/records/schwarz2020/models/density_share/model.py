def run(inputs, settings):
    return {"share": 100.0 * inputs["rho"] / inputs["total"]}


def symbolic():
    import sympy as sp
    rho, total = sp.symbols("rho total", positive=True)
    return {"share": 100 * rho / total}
