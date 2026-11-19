# Eq. 1 applied to the critical strain for the onset of creases, which the paper says
# satisfies the same relation (Sec. 2, citing Ref. 39): 1 - e^PE = sqrt(lambda3)(1 - e),
# lambda3 = 1/sqrt(lambda1), lambda1 = 1 - e. Dimensionless.
import math


def run(inputs, settings):
    e = inputs["e_uni"]
    return {"e_pe": 1.0 - math.sqrt(1.0 / math.sqrt(1.0 - e)) * (1.0 - e)}


def symbolic():
    import sympy as sp
    e_uni = sp.symbols("e_uni", positive=True)
    return {"e_pe": 1 - sp.sqrt(1 / sp.sqrt(1 - e_uni)) * (1 - e_uni)}
