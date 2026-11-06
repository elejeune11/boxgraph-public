# Eq. 5 solved for the multiplier: c = p/p0.


def run(inputs, settings):
    return {"c": inputs["p"] / inputs["p0"]}


def symbolic():
    import sympy as sp
    p, p0 = sp.symbols("p p0", positive=True)
    return {"c": p / p0}
