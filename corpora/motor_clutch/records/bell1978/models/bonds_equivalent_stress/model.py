def run(inputs, settings):
    return {"n": inputs["sigma"] / inputs["fc"]}


def symbolic():
    import sympy as sp
    sigma, fc = sp.symbols("sigma fc", positive=True)
    return {"n": sigma / fc}
