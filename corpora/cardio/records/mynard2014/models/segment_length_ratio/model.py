def run(inputs, settings):
    return {"ratio": (inputs["W_a"] / inputs["W_n"]) ** inputs["b"]}


def symbolic():
    import sympy as sp
    W_a, W_n, b = sp.symbols("W_a W_n b", positive=True)
    return {"ratio": (W_a / W_n) ** b}
