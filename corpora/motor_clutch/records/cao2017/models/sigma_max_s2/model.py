def run(inputs, settings):
    a, b = inputs["alpha"], inputs["beta"]
    return {"sigma_max": b * inputs["rho0"] / (b - a)}


def symbolic():
    import sympy as sp
    rho0, alpha, beta = sp.symbols("rho0 alpha beta", positive=True)
    return {"sigma_max": beta * rho0 / (beta - alpha)}
