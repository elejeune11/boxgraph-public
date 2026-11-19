def run(inputs, settings):
    return {"ratio": inputs["K"] / inputs["Kcap"]}


def symbolic():
    import sympy as sp
    K, Kc = sp.symbols("K Kcap", positive=True)
    return {"ratio": K / Kc}
