# Energy density of the Hookean shell energy (3): E = 2 pi int e r0 ds. Lengths in units of R, E in a stress unit.


def run(inputs, settings):
    Em, eps, nu = inputs["Em"], inputs["eps"], inputs["nu"]
    Es, Ep, Ks, Kp = inputs["Es"], inputs["Ephi"], inputs["Ks"], inputs["Kphi"]
    st = Em * eps / (2 * (1 - nu**2)) * (Es**2 + Ep**2 + 2 * nu * Es * Ep)
    bd = Em * eps**3 / (24 * (1 - nu**2)) * (Ks**2 + Kp**2 + 2 * nu * Ks * Kp)
    return {"e_stretch": st, "e_bend": bd, "e": st + bd}


def symbolic():
    import sympy as sp
    Em, eps, nu, Es, Ephi, Ks, Kphi = sp.symbols("Em eps nu Es Ephi Ks Kphi", positive=True)
    st = Em * eps / (2 * (1 - nu**2)) * (Es**2 + Ephi**2 + 2 * nu * Es * Ephi)
    bd = Em * eps**3 / (24 * (1 - nu**2)) * (Ks**2 + Kphi**2 + 2 * nu * Ks * Kphi)
    return {"e_stretch": st, "e_bend": bd, "e": st + bd}
