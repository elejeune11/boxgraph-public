def run(inputs, settings):
    return {"d": inputs["V"] * inputs["t"] / 1000.0}  # nm -> um


def symbolic():
    import sympy as sp
    V, t = sp.symbols("V t", positive=True)
    return {"d": V * t / 1000}
