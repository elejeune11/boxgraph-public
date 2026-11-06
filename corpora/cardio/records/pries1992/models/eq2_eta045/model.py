# Eq. 2 of the paper: D in um, output dimensionless.
import math


def run(inputs, settings):
    D = inputs["D"]
    return {"eta045": 220 * math.exp(-1.3 * D) + 3.2 - 2.44 * math.exp(-0.06 * D**0.645)}


def symbolic():
    import sympy as sp
    D = sp.symbols("D", positive=True)
    return {"eta045": 220 * sp.exp(-sp.Rational(13, 10) * D) + sp.Rational(16, 5)
            - sp.Rational(61, 25) * sp.exp(-sp.Rational(3, 50) * D ** sp.Rational(129, 200))}
