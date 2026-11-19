# Eq. (59): eta = kappa_s0 (eps h) / (2 f_s0 f_phi0), the middle form, with eps h the undeformed
# relative thickness. All quantities nondimensional (lengths in units of the embryo radius R).


def run(inputs, settings):
    return {"eta": inputs["kappa_s0"] * inputs["eps_h"] / (2 * inputs["f_s0"] * inputs["f_phi0"])}


def symbolic():
    import sympy as sp
    kappa_s0, eps_h, f_s0, f_phi0 = sp.symbols("kappa_s0 eps_h f_s0 f_phi0", real=True)
    return {"eta": kappa_s0 * eps_h / (2 * f_s0 * f_phi0)}
