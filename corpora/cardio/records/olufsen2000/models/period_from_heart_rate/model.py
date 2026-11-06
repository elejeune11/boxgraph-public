def run(inputs, settings):
    return {"T": 1.0 / inputs["HR"]}


def symbolic():
    import sympy as sp
    HR = sp.symbols("HR", positive=True)
    return {"T": 1 / HR}
