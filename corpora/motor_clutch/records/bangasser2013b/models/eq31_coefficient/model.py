# Eq. 31 with its three factors substituted: C = (Fm/vu)(n/ln n) ln(1/eps), the coefficient of kon.
# Fm/vu in pN*s/nm -> C in pN*s/nm.


def run(inputs, settings):
    return {"C": inputs["ratio"] * inputs["nfac"] * inputs["L"]}


def symbolic():
    import sympy as sp
    ratio, nfac, L = sp.symbols("ratio nfac L", positive=True)
    return {"C": ratio * nfac * L}
