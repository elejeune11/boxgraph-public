def run(inputs, settings):
    return {"N": inputs["n"] / inputs["area"]}


def symbolic():
    import sympy as sp
    n, area = sp.symbols("n area", positive=True)
    return {"N": n / area}
