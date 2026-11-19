def run(inputs, settings):
    return {"ratio": inputs["Ao"] / inputs["Ai"]}


def symbolic():
    import sympy as sp
    Ao, Ai = sp.symbols("Ao Ai", positive=True)
    return {"ratio": Ao / Ai}
