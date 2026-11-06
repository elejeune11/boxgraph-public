def run(inputs, settings):
    return {"N": inputs["K"] * inputs["l"] / inputs["R"]}


def symbolic():
    import sympy as sp
    K, l, R = sp.symbols("K l R", positive=True)
    return {"N": K * l / R}
