# Exact wrinkling bifurcation of a neo-Hookean film on an infinitely deep neo-Hookean
# substrate (Appendix, Eqs. A1-A10), as printed. Plane strain compression with plane
# strain substrate prestretch lam01 (Sec. 3.1, 3.2). The paper says only that the
# eigenvalue problem |E| = 0 "is carried out numerically" and "must be minimized over all
# values of kh"; the numerical scheme below (scan in strain, bisection, minimum over kh)
# is the reader's. All quantities are dimensionless.
import math

import mpmath as mp


def _film_BC(r, kh):
    """B and C of Eqs. A3-A5 for a film layer with traction-free top at x2 = h."""
    q = (r * r + 1) / r  # r^-1 (r^2 + 1)
    M = mp.matrix([[2 * r * mp.e ** (-r * kh), q * mp.e ** (-kh)],
                   [q * mp.e ** (-r * kh), 2 * mp.e ** (-kh)]])
    R = mp.matrix([[-2 * r * mp.e ** (r * kh), -q * mp.e ** kh],
                   [q * mp.e ** (r * kh), 2 * mp.e ** kh]])
    A = M ** -1 * R  # Eq. A3
    A11, A12, A21, A22 = A[0, 0], A[0, 1], A[1, 0], A[1, 1]
    B = mp.matrix([[-2 * r * (1 + A11) - q * A21, -q * (1 + A22) - 2 * r * A12],
                   [q * (1 - A11) - 2 * A21, 2 * (1 - A22) - q * A12]])  # Eq. A4
    C = mp.matrix([[-1 + A11 + A21 / r, -1 / r + A12 + A22 / r],
                   [1 + A11 + A21, 1 + A12 + A22]])  # Eq. A5
    return B, C, mp.det(M)


def _D(rs):
    """D of Eq. A9 (top of the semi-infinite substrate)."""
    return mp.matrix([[rs + 1, -(rs - 1)], [-(rs - 1), (rs + 1) / rs]])


def stretches(e, lam01, loading):
    """Film ratio rf, substrate ratio rs and lam03s for film strain e (Eqs. 1, 3, 4)."""
    lam1f = 1 - e
    lam1s = lam1f * lam01
    if loading == "plane_strain":  # Sec. 3.2: lam3 = 1, lam2 = 1/lam1
        return 1 / lam1f ** 2, 1 / lam1s ** 2, 1.0
    if loading == "uniaxial":  # Sec. 3.3: lam2 = lam3 = 1/sqrt(lam1)
        return lam1f ** -1.5, lam1s ** -1.5, lam01 ** -0.5
    raise ValueError(loading)


def det_E(e, kh, mu_ratio, lam01, loading):
    """Sign of |E| (Eq. A10) times |C| times the determinant of the first matrix of Eq. A3.
    The factor |C| removes the poles of |E| where C is singular; the factor of Eq. A3 removes
    the pole that A, and so B and C, have where that matrix is singular (which happens at
    Biot's surface-wrinkling ratio r). The product has the zeros of |E| and no poles."""
    rf, rs, lam03 = stretches(e, lam01, loading)
    with mp.workdps(30 + int(2.5 * rf * kh / 2.3)):
        B, C, d3 = _film_BC(mp.mpf(rf), mp.mpf(kh))
        M = B - (1 / mp.mpf(lam03)) / mp.mpf(mu_ratio) * _D(mp.mpf(rs)) * C
        d = mp.det(M) * d3
        return float(mp.sign(d))  # only the sign is used


def critical_strain_at(kh, mu_ratio, lam01, loading, s):
    """Smallest film strain e at which |E| = 0 for this kh, or None below e_max."""
    es = [s["e_min"] * (s["e_max"] / s["e_min"]) ** (i / (s["n_e"] - 1)) for i in range(s["n_e"])]
    prev_e, prev = es[0], det_E(es[0], kh, mu_ratio, lam01, loading)
    for e in es[1:]:
        cur = det_E(e, kh, mu_ratio, lam01, loading)
        if cur != prev:
            lo, hi = prev_e, e
            while hi - lo > s["tol"]:
                mid = 0.5 * (lo + hi)
                if det_E(mid, kh, mu_ratio, lam01, loading) == prev:
                    lo = mid
                else:
                    hi = mid
            return 0.5 * (lo + hi)
        prev_e, prev = e, cur
    return None


def solve(mu_ratio, lam01, loading, s):
    lk = [math.log(s["kh_min"]) + (math.log(s["kh_max"]) - math.log(s["kh_min"])) * i / (s["n_kh"] - 1)
          for i in range(s["n_kh"])]
    vals = [critical_strain_at(math.exp(x), mu_ratio, lam01, loading, s) for x in lk]
    big = 10.0
    f = [v if v is not None else big for v in vals]
    i = min(range(len(f)), key=lambda j: (f[j], j))
    # golden-section refinement of the minimum over log kh between the neighbours
    a = lk[max(i - 1, 0)]
    b = lk[min(i + 1, len(lk) - 1)]
    g = (math.sqrt(5) - 1) / 2

    def F(x):
        v = critical_strain_at(math.exp(x), mu_ratio, lam01, loading, s)
        return big if v is None else v

    c, d = b - g * (b - a), a + g * (b - a)
    fc, fd = F(c), F(d)
    for _ in range(s["n_golden"]):
        if fc <= fd:
            b, d, fd = d, c, fc
            c = b - g * (b - a)
            fc = F(c)
        else:
            a, c, fc = c, d, fd
            d = a + g * (b - a)
            fd = F(d)
    x = c if fc <= fd else d
    ew = min(fc, fd, f[i])
    if f[i] < min(fc, fd):
        x = lk[i]
    return ew, math.exp(x)


DEFAULTS = {"kh_min": 1e-3, "kh_max": 30.0, "n_kh": 41, "e_min": 1e-4, "e_max": 0.7,
            "n_e": 120, "tol": 1e-6, "n_golden": 25}


def settings_of(settings):
    s = {**DEFAULTS, **settings}
    for key in ("n_kh", "n_e", "n_golden"):
        s[key] = int(round(s[key]))
    return s


def run(inputs, settings):
    s = settings_of(settings)
    ew, kh = solve(inputs["mu_ratio"], inputs["lam01"], "plane_strain", s)
    return {"eW": ew, "kh": kh}
