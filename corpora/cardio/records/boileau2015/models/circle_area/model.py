# Tables III, V and VII list both rd and Ad; the paper does not write the relation, which for a
# circular lumen (radius r, Eq. 2) is Ad = pi rd^2.
import math


def run(inputs, settings):
    return {"Ad": math.pi * inputs["rd"] ** 2}


def symbolic():
    import sympy as sp
    rd = sp.symbols("rd", positive=True)
    return {"Ad": sp.pi * rd**2}
