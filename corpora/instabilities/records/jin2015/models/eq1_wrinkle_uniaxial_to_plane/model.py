# Eq. 1: 1 - e_m^PE = sqrt(lambda3) (1 - e_m), with the uniaxial compression condition
# lambda3 = 1/sqrt(lambda1) and lambda1 = 1 - e_m (Sec. 2). Dimensionless.
import math


def run(inputs, settings):
    e = inputs["e_uni"]
    lam1 = 1.0 - e
    lam3 = 1.0 / math.sqrt(lam1)
    return {"e_pe": 1.0 - math.sqrt(lam3) * (1.0 - e)}


def symbolic():
    import sympy as sp
    e_uni = sp.symbols("e_uni", positive=True)
    return {"e_pe": 1 - sp.sqrt(1 / sp.sqrt(1 - e_uni)) * (1 - e_uni)}
