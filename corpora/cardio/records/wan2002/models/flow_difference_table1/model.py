def run(inputs, settings):
    return {"diff": 100.0 * (inputs["q1d"] - inputs["q3d"]) / inputs["q3d"]}


def symbolic():
    import sympy as sp
    q1d, q3d = sp.symbols("q1d q3d", positive=True)
    return {"diff": 100 * (q1d - q3d) / q3d}
