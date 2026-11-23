def run(inputs, settings):
    return {"k": inputs["x"] * inputs["k_ref"] / inputs["x_ref"]}


def symbolic():
    import sympy as sp
    x, x_ref, k_ref = sp.symbols("x x_ref k_ref", positive=True)
    return {"k": x * k_ref / x_ref}
