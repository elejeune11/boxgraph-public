import math

from scipy.special import lambertw

EV_NM_DYNE = 1.602176634e-12 / 1e-7  # eV/nm -> dyne


def run(inputs, settings):
    # alpha exp(alpha + 1) = KN2  <=>  alpha = W(KN2 / e)
    alpha = float(lambertw(inputs["KN2"] / math.e).real)
    return {"fc": inputs["kT"] / inputs["r0"] * EV_NM_DYNE * alpha, "alpha_c": alpha}


def symbolic():
    import sympy as sp
    kT, r0, KN2 = sp.symbols("kT r0 KN2", positive=True)
    alpha = sp.LambertW(KN2 / sp.E)
    return {"fc": kT / r0 * EV_NM_DYNE * alpha, "alpha_c": alpha}
