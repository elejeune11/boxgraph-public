# Wrinkling of a neo-Hookean film/substrate bilayer of finite substrate thickness:
# det A = 0 (Eq. B7) with the 8 x 8 matrix A of Eqs. B8-B15, as printed.
# Plane strain: lambda3 = 1. The critical strain e_c = 1 - lambda_c (Appendix B) is the
# smallest compressive strain at which det A changes sign for a given K Hf; e_m is its
# minimum over K Hf, and L_m/Hf = 2 pi/(K Hf) there.
# The paper does not say how it solved Eq. B7; the scheme below (strain scan, bisection,
# grid plus golden-section minimum over log K Hf) is the reader's. Each column of A is
# multiplied by a positive constant (exp(-largest exponent in the column)) so the
# entries stay finite for thick substrates; that leaves the sign of det A, and so its
# zeros, unchanged. All quantities are dimensionless.
import math

import numpy as np


def _matrix(lam1, lam3, KHf, g, r):
    """A of Eqs. B8-B15 with scaled columns. g = Gf/Gs, r = Hs/Hf."""
    mu = lam1 * lam1 * lam3          # lambda1^2 lambda3
    S = lam1 ** 2 + lam1 ** -2 * lam3 ** -2
    P = 1 + lam1 ** 4 * lam3 ** 2
    a = KHf / mu                     # K Hf/(lambda1^2 lambda3)
    b = KHf                          # K Hf
    A_ = KHf * (1 + r) / mu          # K (Hf + Hs)/(lambda1^2 lambda3)
    B_ = KHf * (1 + r)               # K (Hf + Hs)
    m = lam1 * lam1 * lam3
    # each entry: (coefficient, exponent)
    E = {}
    # Eq. B8
    E[1, 1] = (S, 0.0); E[1, 2] = (-S, 0.0); E[1, 3] = (2 / lam3, 0.0); E[1, 4] = (-2 / lam3, 0.0)
    # Eq. B9
    E[2, 1] = (2.0, 0.0); E[2, 2] = (2.0, 0.0); E[2, 3] = (P, 0.0); E[2, 4] = (P, 0.0)
    # Eq. B10
    E[3, 1] = (S * g, a); E[3, 2] = (-S * g, -a)
    E[3, 3] = (2 * g / lam3, b); E[3, 4] = (-2 * g / lam3, -b)
    E[3, 5] = (-S, a); E[3, 6] = (S, -a)
    E[3, 7] = (-2 / lam3, b); E[3, 8] = (2 / lam3, -b)
    # Eq. B11
    E[4, 1] = (2 * g, a); E[4, 2] = (2 * g, -a)
    E[4, 3] = (P * g, b); E[4, 4] = (P * g, -b)
    E[4, 5] = (-2.0, a); E[4, 6] = (-2.0, -a)
    E[4, 7] = (-P, b); E[4, 8] = (-P, -b)
    # Eq. B12: A51 = -A55 = -e^a, A52 = -A56 = e^-a, A53 = -A57 = -e^b m, A54 = -A58 = e^-b m
    E[5, 1] = (-1.0, a); E[5, 5] = (1.0, a)
    E[5, 2] = (1.0, -a); E[5, 6] = (-1.0, -a)
    E[5, 3] = (-m, b); E[5, 7] = (m, b)
    E[5, 4] = (m, -b); E[5, 8] = (-m, -b)
    # Eq. B13: A61 = -A65 = e^a, A62 = -A66 = e^-a, A63 = -A67 = e^b, A64 = -A68 = e^-b
    E[6, 1] = (1.0, a); E[6, 5] = (-1.0, a)
    E[6, 2] = (1.0, -a); E[6, 6] = (-1.0, -a)
    E[6, 3] = (1.0, b); E[6, 7] = (-1.0, b)
    E[6, 4] = (1.0, -b); E[6, 8] = (-1.0, -b)
    # Eq. B14
    E[7, 5] = (2.0, A_); E[7, 6] = (2.0, -A_); E[7, 7] = (P, B_); E[7, 8] = (P, -B_)
    # Eq. B15
    E[8, 5] = (1.0, A_); E[8, 6] = (1.0, -A_); E[8, 7] = (1.0, B_); E[8, 8] = (1.0, -B_)
    M = np.zeros((8, 8))
    for j in range(1, 9):
        col = [(i, c, x) for (i, jj), (c, x) in E.items() if jj == j]
        top = max(x for _, _, x in col)
        for i, c, x in col:
            M[i - 1, j - 1] = c * math.exp(x - top)
    return M


def sign_det(e, KHf, g, r, loading):
    lam1 = 1.0 - e
    lam3 = 1.0 if loading == "plane_strain" else lam1 ** -0.5
    d = np.linalg.det(_matrix(lam1, lam3, KHf, g, r))
    return 1 if d > 0 else (-1 if d < 0 else 0)


def critical_strain_at(KHf, g, r, loading, s):
    """Smallest strain e at which det A changes sign for this K Hf (e_c), or None."""
    n = s["n_e"]
    es = [s["e_min"] * (s["e_max"] / s["e_min"]) ** (i / (n - 1)) for i in range(n)]
    prev_e, prev = es[0], sign_det(es[0], KHf, g, r, loading)
    for e in es[1:]:
        cur = sign_det(e, KHf, g, r, loading)
        if cur != prev:
            lo, hi = prev_e, e
            while hi - lo > s["tol"]:
                mid = 0.5 * (lo + hi)
                if sign_det(mid, KHf, g, r, loading) == prev:
                    lo = mid
                else:
                    hi = mid
            return 0.5 * (lo + hi)
        prev_e, prev = e, cur
    return None


def minimum(g, r, loading, s):
    """(e_m, K Hf at the minimum) of e_c over K Hf."""
    big = 10.0
    lk = [math.log(s["kh_min"]) + (math.log(s["kh_max"]) - math.log(s["kh_min"])) * i / (s["n_kh"] - 1)
          for i in range(s["n_kh"])]

    def F(x):
        v = critical_strain_at(math.exp(x), g, r, loading, s)
        return big if v is None else v

    f = [F(x) for x in lk]
    i = min(range(len(f)), key=lambda j: (f[j], j))
    a, b = lk[max(i - 1, 0)], lk[min(i + 1, len(lk) - 1)]
    q = (math.sqrt(5) - 1) / 2
    c, d = b - q * (b - a), a + q * (b - a)
    fc, fd = F(c), F(d)
    for _ in range(s["n_golden"]):
        if fc <= fd:
            b, d, fd = d, c, fc
            c = b - q * (b - a)
            fc = F(c)
        else:
            a, c, fc = c, d, fd
            d = a + q * (b - a)
            fd = F(d)
    best = min([(f[i], lk[i]), (fc, c), (fd, d)])
    return best[0], math.exp(best[1])


DEFAULTS = {"kh_min": 0.01, "kh_max": 300.0, "n_kh": 61, "e_min": 1e-4, "e_max": 0.75,
            "n_e": 150, "tol": 1e-7, "n_golden": 30}


def settings_of(settings):
    s = {**DEFAULTS, **settings}
    for key in ("n_kh", "n_e", "n_golden"):
        s[key] = int(round(s[key]))
    return s


def solve(g, r, loading, settings):
    s = settings_of(settings)
    em, KHf = minimum(g, r, loading, s)
    return {"em": em, "Lm": 2 * math.pi / KHf}


def run(inputs, settings):
    return solve(inputs["Gf_Gs"], inputs["Hs_Hf"], "plane_strain", settings)
