# Eq. 6: kappa_s^opt = C2 nc Fb kon / vu / (1 - C3 kon nc Fb / (koff nm Fm)).
# pN * (1/s) / (nm/s) = pN/nm.


def run(inputs, settings):
    i = inputs
    return {"ks_opt": i["C2"] * i["nc"] * i["Fb"] * i["kon"] / i["vu"]
            / (1 - i["C3"] * i["kon"] * i["nc"] * i["Fb"] / (i["koff"] * i["nm"] * i["Fm"]))}


def symbolic():
    import sympy as sp
    C2, C3, nc, Fb, kon, vu, koff, nm, Fm = sp.symbols("C2 C3 nc Fb kon vu koff nm Fm", positive=True)
    return {"ks_opt": C2 * nc * Fb * kon / vu / (1 - C3 * kon * nc * Fb / (koff * nm * Fm))}
