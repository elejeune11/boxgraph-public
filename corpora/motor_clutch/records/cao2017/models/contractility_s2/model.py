# Stresses in kPa; alpha and beta arrive in 1/Pa and are used per kPa (x 1000).


def run(inputs, settings):
    a, b = inputs["alpha"] * 1e3, inputs["beta"] * 1e3
    K, rho0, Keff = inputs["K"], inputs["rho0"], inputs["Keff"]
    g = K * b - 1.0
    return {"sigma": 1.0 / (1.0 / Keff + (b - a) / g) * b * rho0 / g}


def symbolic():
    import sympy as sp
    Keff, K, rho0, alpha, beta = sp.symbols("Keff K rho0 alpha beta", positive=True)
    a, b = alpha * 1000, beta * 1000
    g = K * b - 1
    return {"sigma": 1 / (1 / Keff + (b - a) / g) * b * rho0 / g}
