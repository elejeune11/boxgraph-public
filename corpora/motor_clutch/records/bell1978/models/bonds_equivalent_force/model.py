def run(inputs, settings):
    return {"n": inputs["F"] / inputs["fc"]}


def symbolic():
    import sympy as sp
    F, fc = sp.symbols("F fc", positive=True)
    return {"n": F / fc}
