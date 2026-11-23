def run(inputs, settings):
    return {"A": inputs["w"] * inputs["h"]}


def symbolic():
    import sympy as sp
    w, h = sp.symbols("w h", positive=True)
    return {"A": w * h}
