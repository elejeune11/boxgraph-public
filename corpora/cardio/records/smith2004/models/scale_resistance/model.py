def run(inputs, settings):
    return {"R_scaled": inputs["factor"] * inputs["R"]}


def symbolic():
    import sympy as sp
    R, factor = sp.symbols("R factor", positive=True)
    return {"R_scaled": factor * R}
