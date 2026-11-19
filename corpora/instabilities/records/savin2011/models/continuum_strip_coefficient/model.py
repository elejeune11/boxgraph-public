# SI footnote 3: b1par h = k1 (2 a1)^3/12 in continuum mechanics, i.e. c = w^3/12 for a strip of width w a1.


def run(inputs, settings):
    return {"c": inputs["w"] ** 3 / 12.0}


def symbolic():
    import sympy as sp
    w = sp.symbols("w", positive=True)
    return {"c": w**3 / 12}
