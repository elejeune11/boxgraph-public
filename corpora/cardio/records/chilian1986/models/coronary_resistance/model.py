def run(inputs, settings):
    return {"R": inputs["P"] / inputs["Q"]}


def symbolic():
    import sympy as sp
    P, Q = sp.symbols("P Q", positive=True)
    return {"R": P / Q}
