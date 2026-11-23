def run(inputs, settings):
    return {"eta": inputs["x"] * inputs["eta_ref"] / inputs["x_ref"]}


def symbolic():
    import sympy as sp
    x, x_ref, eta_ref = sp.symbols("x x_ref eta_ref", positive=True)
    return {"eta": x * eta_ref / x_ref}
