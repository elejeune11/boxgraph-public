# A resistance multiplied by a factor.


def run(inputs, settings):
    return {"R_scaled": inputs["R"] * inputs["factor"]}


def symbolic():
    import sympy as sp
    R, factor = sp.symbols("R factor", positive=True)
    return {"R_scaled": R * factor}
