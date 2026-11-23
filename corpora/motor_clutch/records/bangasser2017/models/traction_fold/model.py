def run(inputs, settings):
    return {"fold": inputs["F_high"] / inputs["F_low"]}


def symbolic():
    import sympy as sp
    F_high, F_low = sp.symbols("F_high F_low", positive=True)
    return {"fold": F_high / F_low}
