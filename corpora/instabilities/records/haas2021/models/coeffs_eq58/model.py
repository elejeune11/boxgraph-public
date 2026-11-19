# Coefficient functions of the large-bending energy density, Eqs. (58a)-(58j), as printed.
# They have removable singularities at eta = 0 (terms like atanh(eta)/eta^3 cancel against
# rational terms), so they are evaluated in 60-digit arithmetic (mpmath); at eta = 0 exactly
# the value is the limit. Inputs and outputs are dimensionless.
import mpmath as mp

NAMES = ("a_ss", "a_sphi", "a_phiphi", "b_ss", "b_sphi", "b_phis", "b_phiphi",
         "g_ss", "g_sphi", "g_phiphi")


def _forms(e):
    q = 1 - e**2
    at = mp.atanh(e)
    return {
        "a_ss": (e**4 - 2 * e**2 + 2) / q**2 + 2 * at / e,
        "a_sphi": 1 / q**2 + at / e,
        "a_phiphi": (3 * e**4 - 6 * e**2 + 4) / q**2,
        "b_ss": -e * (2 - e**2) / (2 * q**2),
        "b_sphi": (e**6 + 4 * e**4 - 11 * e**2 + 3) / (18 * e * q**2) - at / (6 * e**2),
        "b_phis": -1 / (2 * e * q**2) + at / (2 * e**2),
        "b_phiphi": (3 * e**5 - 5 * e**3 + e) / (6 * q**2),
        "g_ss": (e**4 - 2 * e**2 + 2) / (4 * e**2 * q**2) - at / (2 * e**3),
        "g_sphi": (e**6 - 2 * e**4 + e**2 + 3) / (36 * e**2 * q**2) - at / (12 * e**3),
        "g_phiphi": (10 * e**4 - 21 * e**2 + 12) / (36 * q**2),
    }


def coefficients(eta):
    """All ten coefficients at eta (|eta| < 1), as mpmath numbers."""
    with mp.workdps(60):
        e = mp.mpf(eta)
        if e == 0:  # removable singularity: the limit
            return {k: mp.limit(lambda x, k=k: _forms(x)[k], 0) for k in NAMES}
        return _forms(e)


def run(inputs, settings):
    eta = inputs["eta"]
    if not -1 < eta < 1:
        return {k: None for k in NAMES}
    c = coefficients(eta)
    return {k: float(c[k]) for k in NAMES}
