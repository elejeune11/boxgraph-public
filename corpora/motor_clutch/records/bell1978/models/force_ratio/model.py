def run(inputs, settings):
    return {"ratio": inputs["f0"] / inputs["fc"]}


def symbolic():
    import sympy as sp
    f0, fc = sp.symbols("f0 fc", positive=True)
    return {"ratio": f0 / fc}
