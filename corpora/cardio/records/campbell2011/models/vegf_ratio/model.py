def run(inputs, settings):
    return {"ratio": inputs["R1"] / inputs["A"]}


def symbolic():
    import sympy as sp
    R1, A = sp.symbols("R1 A", positive=True)
    return {"ratio": R1 / A}
