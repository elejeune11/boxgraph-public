# Young's modulus of the neo-Hookean material of Eq. (26), e = (C/2)(I1 - 3), in units of C. At small
# strain this energy has shear modulus mu = C, and E = 2 mu (1 + nu).


def run(inputs, settings):
    return {"E_over_C": 2 * (1 + inputs["nu"])}


def symbolic():
    import sympy as sp
    nu = sp.Symbol("nu", positive=True)
    return {"E_over_C": 2 * (1 + nu)}
