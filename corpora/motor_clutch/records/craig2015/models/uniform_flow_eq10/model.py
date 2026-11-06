def run(inputs, settings):
    F = inputs["F"]
    return {"V": F / (1 + inputs["b"] * F)}


def symbolic():
    import sympy as sp
    F, b = sp.symbols("F b", positive=True)
    return {"V": F / (1 + b * F)}
