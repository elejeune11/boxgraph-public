# Eq. 1 as printed; D in um.
import math


def run(inputs, settings):
    D, HD = inputs["D"], inputs["HD"]
    return {"HT_HD": HD + (1 - HD) * (1 + 1.7 * math.exp(-0.415 * D) - 0.6 * math.exp(-0.011 * D))}


def symbolic():
    import sympy as sp
    D, HD = sp.symbols("D HD", positive=True)
    return {"HT_HD": HD + (1 - HD) * (1 + sp.Float("1.7") * sp.exp(-sp.Float("0.415") * D)
                                      - sp.Float("0.6") * sp.exp(-sp.Float("0.011") * D))}
