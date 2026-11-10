# Fold change b / a. Port units: mmHg/ml in, dimensionless out.


def run(inputs, settings):
    return {"fold": inputs["b"] / inputs["a"]}


def symbolic():
    import sympy as sp
    a, b = sp.symbols("a b", positive=True)
    return {"fold": b / a}
