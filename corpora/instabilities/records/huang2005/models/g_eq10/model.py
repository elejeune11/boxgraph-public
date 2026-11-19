# Eq. 10, evaluated in 50-digit arithmetic so that the thin-substrate limit (where the denominator is a
# small difference of large terms) and the thick-substrate limit (where cosh and sinh overflow a float)
# are both exact to double precision. The formula is the printed one; only the arithmetic is careful.
import mpmath


def g_mp(kH, nu_s):
    """Eq. 10 at mpmath precision (kH and nu_s are mpf)."""
    y = 2 * kH
    if y > 200:  # cosh/sinh -> 1 to far below double precision; the ratio of the leading terms
        num = (3 - 4 * nu_s) + 2 * (5 - 12 * nu_s + 8 * nu_s ** 2 + 2 * kH ** 2) * mpmath.exp(-y)
        den = (6 - 8 * nu_s) - 8 * kH * mpmath.exp(-y)
        return num / den
    num = (3 - 4 * nu_s) * mpmath.cosh(y) + 5 - 12 * nu_s + 8 * nu_s ** 2 + 2 * kH ** 2
    den = (6 - 8 * nu_s) * mpmath.sinh(y) - 4 * kH
    return num / den


def run(inputs, settings):
    with mpmath.workdps(60):
        g = g_mp(mpmath.mpf(inputs["kH"]), mpmath.mpf(inputs["nu_s"]))
        return {"g": float(g)}


def symbolic():
    import sympy as sp
    kH, nu_s = sp.symbols("kH nu_s", positive=True)
    num = (3 - 4 * nu_s) * sp.cosh(2 * kH) + 5 - 12 * nu_s + 8 * nu_s ** 2 + 2 * kH ** 2
    den = (6 - 8 * nu_s) * sp.sinh(2 * kH) - 4 * kH
    return {"g": num / den}
