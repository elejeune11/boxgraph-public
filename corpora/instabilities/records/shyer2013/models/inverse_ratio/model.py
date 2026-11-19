def run(inputs, settings):
    return {"factor": 1.0 / inputs["ratio"]}


def symbolic():
    import sympy as sp
    ratio = sp.symbols("ratio", positive=True)
    return {"factor": 1 / ratio}
