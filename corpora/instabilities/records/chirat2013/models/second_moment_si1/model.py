def run(inputs, settings):
    return {"I": inputs["w"] * inputs["h"] ** 3 / 12.0}


def symbolic():
    import sympy as sp
    w, h = sp.symbols("w h", positive=True)
    return {"I": w * h**3 / 12}
