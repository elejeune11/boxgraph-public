def run(inputs, settings):
    return {"eps": inputs["V0"] / (inputs["r"] * inputs["L0"])}


def symbolic():
    import sympy as sp
    V0, r, L0 = sp.symbols("V0 r L0", positive=True)
    return {"eps": V0 / (r * L0)}
