# Wrinkling bifurcation of a neo-Hookean film bonded on a deep neo-Hookean substrate that was
# prestretched by lambda_p, under plane-strain compression e = DL/L (film stretch 1 - e,
# substrate stretch lambda_p (1 - e)). The paper performs this linear stability analysis
# "following Cao and Hutchinson [29]" and does not print the equations; this is Cao and
# Hutchinson's eigenvalue problem (their Appendix, Eqs. A1-A10), the same solver as the
# corpus record cao2012/bilayer_plane_strain. The numerical scheme (scan in strain, bisection,
# minimum over kh) is the reader's. All quantities are dimensionless.
import math

import mpmath as mp


def _film_BC(r, kh):
    """B and C for a film layer with a traction-free top at x2 = h."""
    q = (r * r + 1) / r
    M = mp.matrix([[2 * r * mp.e ** (-r * kh), q * mp.e ** (-kh)],
                   [q * mp.e ** (-r * kh), 2 * mp.e ** (-kh)]])
    R = mp.matrix([[-2 * r * mp.e ** (r * kh), -q * mp.e ** kh],
                   [q * mp.e ** (r * kh), 2 * mp.e ** kh]])
    A = M ** -1 * R
    A11, A12, A21, A22 = A[0, 0], A[0, 1], A[1, 0], A[1, 1]
    B = mp.matrix([[-2 * r * (1 + A11) - q * A21, -q * (1 + A22) - 2 * r * A12],
                   [q * (1 - A11) - 2 * A21, 2 * (1 - A22) - q * A12]])
    C = mp.matrix([[-1 + A11 + A21 / r, -1 / r + A12 + A22 / r],
                   [1 + A11 + A21, 1 + A12 + A22]])
    return B, C, mp.det(M)


def _D(rs):
    """Top of the semi-infinite substrate."""
    return mp.matrix([[rs + 1, -(rs - 1)], [-(rs - 1), (rs + 1) / rs]])


def det_sign(e, kh, mu_ratio, lam_p):
    """Sign of the pole-free bifurcation determinant at film strain e (plane strain)."""
    lam1f = 1 - e
    rf, rs = 1 / lam1f ** 2, 1 / (lam1f * lam_p) ** 2
    with mp.workdps(30 + int(2.5 * rf * kh / 2.3)):
        B, C, d3 = _film_BC(mp.mpf(rf), mp.mpf(kh))
        M = B - 1 / mp.mpf(mu_ratio) * _D(mp.mpf(rs)) * C
        return float(mp.sign(mp.det(M) * d3))


def critical_strain_at(kh, mu_ratio, lam_p, s):
    """Smallest film strain at which the determinant changes sign for this kh, or None."""
    es = [s["e_min"] * (s["e_max"] / s["e_min"]) ** (i / (s["n_e"] - 1)) for i in range(s["n_e"])]
    prev_e, prev = es[0], det_sign(es[0], kh, mu_ratio, lam_p)
    for e in es[1:]:
        cur = det_sign(e, kh, mu_ratio, lam_p)
        if cur != prev:
            lo, hi = prev_e, e
            while hi - lo > s["tol"]:
                mid = 0.5 * (lo + hi)
                if det_sign(mid, kh, mu_ratio, lam_p) == prev:
                    lo = mid
                else:
                    hi = mid
            return 0.5 * (lo + hi)
        prev_e, prev = e, cur
    return None


def solve(mu_ratio, lam_p, s):
    """Critical strain minimized over kh, and the kh at the minimum."""
    lk = [math.log(s["kh_min"]) + (math.log(s["kh_max"]) - math.log(s["kh_min"])) * i / (s["n_kh"] - 1)
          for i in range(s["n_kh"])]
    big = 10.0

    def F(x):
        v = critical_strain_at(math.exp(x), mu_ratio, lam_p, s)
        return big if v is None else v

    f = [F(x) for x in lk]
    i = min(range(len(f)), key=lambda j: (f[j], j))
    a, b = lk[max(i - 1, 0)], lk[min(i + 1, len(lk) - 1)]
    g = (math.sqrt(5) - 1) / 2
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
    ew, kh = solve(inputs["mu_ratio"], inputs["lam_p"], settings_of(settings))
    return {"e_wrinkle": ew, "kh": kh}
