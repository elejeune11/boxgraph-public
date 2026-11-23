# Supp. eqns 11 and 13: steady-state bound clutches and actin velocity relative to the adhesion.
# pN / (pN/nm) * 1/s = nm/s; alpha_c [1/(pN s)] * Ftot [pN] is a rate in 1/s.


def run(inputs, settings):
    F, kon, k0 = inputs["Ftot"], inputs["kon"], inputs["k0"]
    kap, Ct, a = inputs["kappa"], inputs["Ct"], inputs["alpha_c"]
    D = kon * Ct - a * F
    Cb = D / (kon + k0)
    if k0 <= -a * F / Ct:  # the stated condition koff > 0, "also applies to eqn. 13"
        v = 0.0
    else:
        v = F * (kon + k0) / (kap * D) * (k0 + a * F * (kon + k0) / D)
    return {"v": v, "Cb": Cb}


def symbolic():
    import sympy as sp
    F, kon, k0, kap, Ct = sp.symbols("Ftot kon k0 kappa Ct", positive=True)
    a = sp.Symbol("alpha_c", real=True)
    D = kon * Ct - a * F
    v = F * (kon + k0) / (kap * D) * (k0 + a * F * (kon + k0) / D)
    return {"v": sp.Piecewise((0, k0 <= -a * F / Ct), (v, True)), "Cb": D / (kon + k0)}
