# Supp. eqn. 14: eqn. 12 with Cb = Ct.


def run(inputs, settings):
    F, k0, kap, Ct, a = inputs["Ftot"], inputs["k0"], inputs["kappa"], inputs["Ct"], inputs["alpha_c"]
    if k0 <= -a * F / Ct:
        return {"v": 0.0}
    return {"v": F / (Ct * kap) * (k0 + a * F / Ct)}


def symbolic():
    import sympy as sp
    F, k0, kap, Ct = sp.symbols("Ftot k0 kappa Ct", positive=True)
    a = sp.Symbol("alpha_c", real=True)
    return {"v": sp.Piecewise((0, k0 <= -a * F / Ct), (F / (Ct * kap) * (k0 + a * F / Ct), True))}
