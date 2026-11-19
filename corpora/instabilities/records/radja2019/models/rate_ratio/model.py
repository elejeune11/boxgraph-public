def run(inputs, settings):
    return {"ratio": inputs["q_forward"] / inputs["q_reverse"]}


def symbolic():
    import sympy as sp
    a, b = sp.symbols("q_forward q_reverse", positive=True)
    return {"ratio": a / b}
