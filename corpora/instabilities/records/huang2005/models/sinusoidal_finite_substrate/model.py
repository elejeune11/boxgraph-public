# Sinusoidal wrinkles on a substrate of finite thickness (Section 3): minimize the printed
# f(kh) = (kh)^2/12 + g(kH, nu_s) Es_bar / ((kh) E_bar)   (Eq. 13), with g from Eq. 10,
# over the wave number; then N_c = h E_bar f_min, lambda_eq = 2 pi / k_eq, and from Eq. 16
# A_eq = (2/k_eq) sqrt((|N|-N_c)/(E_bar h)) = h * [2 sqrt(f_min)/(k_eq h)] * sqrt(|N|/N_c - 1).
# The last bracket is the "normalized amplitude" of Fig. 5. Arithmetic in 60 digits (see g_eq10).
import mpmath

DPS = 60


def g_mp(kH, nu_s):
    """Eq. 10 (the same formula as model g_eq10)."""
    y = 2 * kH
    if y > 200:
        num = (3 - 4 * nu_s) + 2 * (5 - 12 * nu_s + 8 * nu_s ** 2 + 2 * kH ** 2) * mpmath.exp(-y)
        den = (6 - 8 * nu_s) - 8 * kH * mpmath.exp(-y)
        return num / den
    num = (3 - 4 * nu_s) * mpmath.cosh(y) + 5 - 12 * nu_s + 8 * nu_s ** 2 + 2 * kH ** 2
    den = (6 - 8 * nu_s) * mpmath.sinh(y) - 4 * kH
    return num / den


def _minimize(ratio, Hh, nu_s, n_grid):
    """k_eq h and f_min, with ratio = E_bar / Es_bar."""
    def f(x):
        return x ** 2 / 12 + g_mp(x * Hh, nu_s) / (x * ratio)

    lo, hi = mpmath.mpf("1e-6"), mpmath.mpf("1e8")
    xs = [lo * (hi / lo) ** (mpmath.mpf(i) / (n_grid - 1)) for i in range(n_grid)]
    fs = [f(x) for x in xs]
    i = min(range(n_grid), key=lambda j: fs[j])
    if i == 0 or i == n_grid - 1:
        raise ValueError("minimum of f at the end of the search range")
    a, b = xs[i - 1], xs[i + 1]
    # golden-section search on f in high precision: f is smooth and has one minimum in [a, b]
    gr = (mpmath.sqrt(5) - 1) / 2
    c, d = b - gr * (b - a), a + gr * (b - a)
    fc, fd = f(c), f(d)
    for _ in range(200):
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - gr * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + gr * (b - a)
            fd = f(d)
        if (b - a) / (a + b) < mpmath.mpf(10) ** (-25):
            break
    x = (a + b) / 2
    return x, f(x)


def run(inputs, settings):
    n_grid = int(settings.get("n_grid", 561))
    with mpmath.workdps(DPS):
        ratio = mpmath.mpf(inputs["Ebar_over_Esbar"])
        Hh = mpmath.mpf(inputs["H_over_h"])
        nu_s = mpmath.mpf(inputs["nu_s"])
        x, fmin = _minimize(ratio, Hh, nu_s, n_grid)
        return {
            "lam_over_h": float(2 * mpmath.pi / x),
            "Nc_over_hE": float(fmin),
            "amp_coeff": float(2 * mpmath.sqrt(fmin) / x),
        }
