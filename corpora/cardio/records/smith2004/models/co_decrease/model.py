def run(inputs, settings):
    return {"decrease": 100.0 * (1.0 - inputs["CO_test"] / inputs["CO_ref"])}


def symbolic():
    import sympy as sp
    a, b = sp.symbols("CO_ref CO_test", positive=True)
    return {"decrease": 100 * (1 - b / a)}
