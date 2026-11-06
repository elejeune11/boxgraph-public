# Momentum-correction coefficient of the profile law s(x) = zeta^-1 (zeta + 2)(1 - x^zeta) (p. 4):
# alpha = (zeta + 2)/(zeta + 1).


def run(inputs, settings):
    z = inputs["zeta"]
    return {"alpha": (z + 2.0) / (z + 1.0)}


def symbolic():
    import sympy as sp
    z = sp.symbols("zeta", positive=True)
    return {"alpha": (z + 2) / (z + 1)}
