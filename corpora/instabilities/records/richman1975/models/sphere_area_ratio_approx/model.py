def run(inputs, settings):
    R, t = inputs["R"], inputs["t"]
    return {"ratio": R / (R - 2 * t), "denominator": R - 2 * t}


def symbolic():
    import sympy as sp
    R, t = sp.symbols("R t", positive=True)
    return {"ratio": R / (R - 2 * t), "denominator": R - 2 * t}
