# Biot's equibiaxial threshold (model biot_equibiaxial) as the paper compares it with Fig. 3(b): the
# same constant at every film thickness, since it has no length-scale (pp. 2, 4).


def run(inputs, settings):
    return {"e_c": 1.0 - inputs["lam_prod"] ** (1.0 / 3.0)}


def symbolic():
    import sympy as sp
    lam_prod, h = sp.symbols("lam_prod h", positive=True)
    return {"e_c": 1 - lam_prod ** sp.Rational(1, 3) + 0 * h}
