def run(inputs, settings):
    f = inputs["s"] / 100.0  # percent -> fraction
    return {"c_up": inputs["c"] * (1 + f), "c_down": inputs["c"] * (1 - f)}


def symbolic():
    import sympy as sp
    c, s = sp.symbols("c s", positive=True)
    return {"c_up": c * (1 + s / 100), "c_down": c * (1 - s / 100)}
