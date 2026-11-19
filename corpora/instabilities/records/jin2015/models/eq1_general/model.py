# Eq. 1 for an arbitrary constant lambda3 (Sec. 2: "for an arbitrary constant lambda3, if we replace
# the variable lambda1 by lambda1 sqrt(lambda3) ... the equation recovers the one under plane strain"):
# 1 - e_c^PE = sqrt(lambda3) (1 - e_c), solved for e_c. Dimensionless.
import math


def run(inputs, settings):
    return {"e_c": 1.0 - (1.0 - inputs["e_pe"]) / math.sqrt(inputs["lam3"])}


def symbolic():
    import sympy as sp
    e_pe, lam3 = sp.symbols("e_pe lam3", positive=True)
    return {"e_c": 1 - (1 - e_pe) / sp.sqrt(lam3)}
