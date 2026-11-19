# Eqs. 9-12 as printed, written in the abscissa of Fig. 5A, s = (1 - eM)/(1 - eC_wrinkle).
# half_lam_pd is Eq. 11 divided by two: Fig. 5A plots the half wavelength of period-doubles.


def run(inputs, settings):
    s = inputs["s"]
    return {"lam_wrinkle": s, "lam_fold": s, "lam_pd": 2.0 * s, "half_lam_pd": s, "lam_ridge": s}


def symbolic():
    import sympy as sp
    s = sp.symbols("s", positive=True)
    return {"lam_wrinkle": s, "lam_fold": s, "lam_pd": 2 * s, "half_lam_pd": s, "lam_ridge": s}
