# L_d ~ lambda_d^2 gamma^(1/2) / t, a scaling law printed with "~": evaluated with prefactor 1. SI units.


def run(inputs, settings):
    return {"Ld": inputs["lam_d"] ** 2 * inputs["gamma"] ** 0.5 / inputs["t"]}


def symbolic():
    import sympy as sp
    lam_d, gamma, t = sp.symbols("lam_d gamma t", positive=True)
    return {"Ld": lam_d**2 * sp.sqrt(gamma) / t}
