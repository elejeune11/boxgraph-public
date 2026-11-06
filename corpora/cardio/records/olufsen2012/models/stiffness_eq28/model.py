def run(inputs, settings):
    return {"Eh_r0": 3.0 / (4.0 * inputs["epsilon"])}


def symbolic():
    import sympy as sp
    epsilon = sp.symbols("epsilon", positive=True)
    return {"Eh_r0": sp.Rational(3, 4) / epsilon}
