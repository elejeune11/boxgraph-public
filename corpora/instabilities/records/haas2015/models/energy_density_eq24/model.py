# Energy density of the Hookean shell energy (2.4): E = 2 pi int e r ds. Lengths in units of R.


def run(inputs, settings):
    Em, h, nu = inputs["Em"], inputs["h"], inputs["nu"]
    Es, Ep, Ks, Kp = inputs["Es"], inputs["Ephi"], inputs["Ks"], inputs["Kphi"]
    st = Em * h / (2 * (1 - nu**2)) * (Es**2 + Ep**2 + 2 * nu * Es * Ep)
    bd = Em * h**3 / (24 * (1 - nu**2)) * (Ks**2 + Kp**2 + 2 * nu * Ks * Kp)
    return {"e_stretch": st, "e_bend": bd, "e": st + bd}


def symbolic():
    import sympy as sp
    Em, h, nu, Es, Ephi, Ks, Kphi = sp.symbols("Em h nu Es Ephi Ks Kphi", positive=True)
    st = Em * h / (2 * (1 - nu**2)) * (Es**2 + Ephi**2 + 2 * nu * Es * Ephi)
    bd = Em * h**3 / (24 * (1 - nu**2)) * (Ks**2 + Kphi**2 + 2 * nu * Ks * Kphi)
    return {"e_stretch": st, "e_bend": bd, "e": st + bd}
