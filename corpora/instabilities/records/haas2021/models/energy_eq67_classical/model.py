# Classical (small-bending) shell energy density, Eq. (67), and its stretching and bending parts,
# Eqs. (69a) and (69b). Nondimensional, as energy_eq63.

OUT = ("e0_stretch", "e0_bend", "e0")


def run(inputs, settings):
    C, eps, h = inputs["C"], inputs["eps"], inputs["h"]
    Es, Ep, Ks, Kp = inputs["Es"], inputs["Ephi"], inputs["Ks"], inputs["Kphi"]
    st = 0.5 * (4 * C * h) * eps**3 * (Es**2 + Es * Ep + Ep**2)
    bd = 0.5 * (C * h**3 / 3) * eps**3 * (Ks**2 + Ks * Kp + Kp**2)
    e0 = 2 * C * eps**3 * (h * (Es**2 + Es * Ep + Ep**2) + h**3 / 12 * (Ks**2 + Ks * Kp + Kp**2))
    return {"e0_stretch": st, "e0_bend": bd, "e0": e0}


def symbolic():
    import sympy as sp
    C, eps, h, Es, Ephi, Ks, Kphi = sp.symbols("C eps h Es Ephi Ks Kphi", positive=True)
    st = sp.Rational(1, 2) * (4 * C * h) * eps**3 * (Es**2 + Es * Ephi + Ephi**2)
    bd = sp.Rational(1, 2) * (C * h**3 / 3) * eps**3 * (Ks**2 + Ks * Kphi + Kphi**2)
    e0 = 2 * C * eps**3 * (h * (Es**2 + Es * Ephi + Ephi**2) + h**3 / 12 * (Ks**2 + Ks * Kphi + Kphi**2))
    return {"e0_stretch": st, "e0_bend": bd, "e0": e0}
