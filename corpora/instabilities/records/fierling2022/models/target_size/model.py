# A_0/A_i from epsilon_a = (A_i - A_0)/A_0 (main text, p. 4). theta only places the value on the
# cross-section (inside the midline band); it does not enter.


def run(inputs, settings):
    return {"s": 1.0 / (1.0 + inputs["eps"])}


def symbolic():
    import sympy as sp
    eps = sp.symbols("eps", positive=True)
    return {"s": 1 / (1 + eps)}
