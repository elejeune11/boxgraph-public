# Eq. (59) solved for the bend-region curvature at which |eta| reaches a given value:
# eta = kappa_s0 (eps h) / (2 f_s0 f_phi0) with kappa_s0 = kappa_b = -k < 0, so k = 2 f_s0 f_phi0 |eta| / (eps h).
# The line of Fig. 5(g) is vertical: k does not depend on the posterior displacement d, which is an
# input only so that the line can be compared at the d positions where it was read.


def run(inputs, settings):
    return {"k": 2 * inputs["f_s0"] * inputs["f_phi0"] * inputs["abs_eta"] / inputs["eps_h"]}


def symbolic():
    import sympy as sp
    abs_eta, eps_h, f_s0, f_phi0 = sp.symbols("abs_eta eps_h f_s0 f_phi0", positive=True)
    return {"k": 2 * f_s0 * f_phi0 * abs_eta / eps_h}
