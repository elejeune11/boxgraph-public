def run(inputs, settings):
    return {"dP": inputs["Q"] / inputs["G"]}


def symbolic():
    import sympy as sp
    Q, G = sp.symbols("Q G", positive=True)
    return {"dP": Q / G}
