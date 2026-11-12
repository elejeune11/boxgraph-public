def run(inputs, settings):
    return {"dp": inputs["rho"] * inputs["g"] * inputs["h"] * 1e-3}


def symbolic():
    import sympy as sp
    rho, g, h = sp.symbols("rho g h", positive=True)
    return {"dp": rho * g * h / 1000}
