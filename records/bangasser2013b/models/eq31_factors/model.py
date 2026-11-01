# The first two factors of Eq. 31 evaluated as on p. 9: Fm/vu and n/ln(n).
# Fm in pN, vu in um/s -> Fm/vu in pN*s/um.
import math


def run(inputs, settings):
    return {"ratio": inputs["Fm"] / inputs["vu"], "nfac": inputs["n"] / math.log(inputs["n"])}


def symbolic():
    import sympy as sp
    Fm, vu, n = sp.symbols("Fm vu n", positive=True)
    return {"ratio": Fm / vu, "nfac": n / sp.log(n)}
