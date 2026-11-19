# Biot's equibiaxial threshold (model biot_equibiaxial) as the paper compares it with Fig. 3(a): the
# same constant at every cross-linker content, since it does not depend on the modulus (pp. 2, 4).


def run(inputs, settings):
    return {"e_c": 1.0 - inputs["lam_prod"] ** (1.0 / 3.0)}


def symbolic():
    import sympy as sp
    lam_prod, c = sp.symbols("lam_prod c", positive=True)
    return {"e_c": 1 - lam_prod ** sp.Rational(1, 3) + 0 * c}
