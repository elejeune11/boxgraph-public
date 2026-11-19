# gb = (1/3)(cbrt(19 + 3 sqrt 33) + cbrt(19 - 3 sqrt 33) + 1), as printed on p. 7 (real cube roots).
import math


def _cbrt(x):
    return math.copysign(abs(x) ** (1.0 / 3.0), x)


def run(inputs, settings):
    s = 3.0 * math.sqrt(33.0)
    return {"gb": (_cbrt(19.0 + s) + _cbrt(19.0 - s) + 1.0) / 3.0}


def symbolic():
    import sympy as sp
    s = 3 * sp.sqrt(33)
    return {"gb": (sp.cbrt(19 + s) + sp.cbrt(19 - s) + 1) / 3}
