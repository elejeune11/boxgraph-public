def run(inputs, settings):
    c0, c1 = inputs["co_measured"], inputs["co_scaled"]
    return {"reduction": 100.0 * (c0 - c1) / c0}


def symbolic():
    import sympy as sp
    c0, c1 = sp.symbols("co_measured co_scaled", positive=True)
    return {"reduction": 100 * (c0 - c1) / c0}
