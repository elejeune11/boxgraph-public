# Eq. S11: kappa_s,m^opt = C2 nc Fb kon / vu; pN (1/s) / (nm/s) = pN/nm.


def run(inputs, settings):
    i = inputs
    return {"ks_opt": i["C2"] * i["nc"] * i["Fb"] * i["kon"] / i["vu"]}


def symbolic():
    import sympy as sp
    C2, nc, Fb, kon, vu = sp.symbols("C2 nc Fb kon vu", positive=True)
    return {"ks_opt": C2 * nc * Fb * kon / vu}
