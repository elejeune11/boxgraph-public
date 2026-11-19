# g^(3/2) = gs (p. 4), so g = gs^(2/3).


def run(inputs, settings):
    return {"gs_biax": inputs["gs"] ** (2.0 / 3.0)}


def symbolic():
    import sympy as sp
    gs = sp.symbols("gs", positive=True)
    return {"gs_biax": gs ** sp.Rational(2, 3)}
