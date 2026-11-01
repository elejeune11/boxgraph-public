KB = 1.380649e-23  # J/K


def run(inputs, settings):
    # J/nm -> pN: 1 J/m = 1e12 pN, and 1 nm = 1e-9 m
    return {"Fb": KB * inputs["T"] / (inputs["xb"] * 1e-9) * 1e12}


def symbolic():
    import sympy as sp
    xb, T = sp.symbols("xb T", positive=True)
    return {"Fb": sp.Float(KB) * T / (xb * sp.Float(1e-9)) * sp.Float(1e12)}
