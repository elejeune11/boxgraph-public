# The unit runs from one venule through the central arteriole to the venule on the other side.


def run(inputs, settings):
    L = 2.0 * inputs["d_av"]
    return {"L_unit": L, "L_necrosis": L}


def symbolic():
    import sympy as sp

    d_av = sp.symbols("d_av", positive=True)
    return {"L_unit": 2 * d_av, "L_necrosis": 2 * d_av}
