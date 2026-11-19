# Stretching and bending moduli of a thin Hookean shell of thickness eps*h, in units of C:
# stretching modulus E (eps h)/(1 - nu^2) = coefficient * C (eps h);
# bending modulus E (eps h)^3/[12 (1 - nu^2)] = C (eps h)^3 / divisor.


def run(inputs, settings):
    E, nu = inputs["E_over_C"], inputs["nu"]
    return {"stretch_coeff": E / (1 - nu**2), "bend_divisor": 12 * (1 - nu**2) / E}


def symbolic():
    import sympy as sp
    E_over_C, nu = sp.symbols("E_over_C nu", positive=True)
    return {"stretch_coeff": E_over_C / (1 - nu**2), "bend_divisor": 12 * (1 - nu**2) / E_over_C}
