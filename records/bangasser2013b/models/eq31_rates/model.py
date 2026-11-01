# Eq. 31 as kappa_s,opt = C kon (C in pN*s/nm), inverted for the on-rate that puts the optimum at
# kappa_s, and koff = kon/q with q = kon/koff.


def run(inputs, settings):
    kon = inputs["ks"] / inputs["C"]
    return {"kon": kon, "koff": kon / inputs["q"]}


def symbolic():
    import sympy as sp
    C, ks, q = sp.symbols("C ks q", positive=True)
    return {"kon": ks / C, "koff": ks / C / q}
