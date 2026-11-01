def run(inputs, settings):
    per_v = inputs["drag"] / inputs["fc"]
    return {"Nb_per_v": per_v, "Nb": per_v * inputs["v"]}


def symbolic():
    import sympy as sp
    drag, fc, v = sp.symbols("drag fc v", positive=True)
    return {"Nb_per_v": drag / fc, "Nb": drag / fc * v}
