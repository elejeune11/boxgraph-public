# Nonlinear (Koiter) stability of the bifurcated wrinkle, Eqs. 2.10-2.12 (pp. 6-7), evaluated along the
# linear bifurcation curve Eq. 2.8 (p. 5), and the M-point: the strain where the energy variation
# delta phi^b / zeta^4 changes sign (positive: progressive wrinkle; negative: instantaneous crease).
#
# Fields as printed: alpha_m Eq. 2.6a, Omega_m Eq. 2.6b, first-order u, p Eqs. 2.5a-c, C1, C2 Eq. A 11,
# second-order displacement through the stream function, Eqs. A 6a-d, A 8, A 9a (exponents beta_m:
# alpha_m with k replaced by 2k). The coefficients B1, B2, F1, F2, F3 and the second-order pressure
# p(2) = Q {H1(X2) cos(2akX1) + H2(X2)} (Eq. 2.9c, exponents as in Eq. B 1) are obtained by solving the
# paper's governing equations (equilibrium of the first Piola-Kirchhoff stress Eq. 2.3 to second order,
# Eq. 2.4, and the traction-free surface, Eq. A 10) numerically by collocation, instead of from the closed
# forms A 9b-d and B 2-B 4. The energy variation is Eq. 2.11 with the two integrals of Eq. 2.12 over one
# period and the half-space. Q0 = a = 1: the sign, and so the M-point, does not depend on them.
import importlib.util
import math
import os

import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("_kbar_eq28", os.path.join(_here, "..", "bifurcation_wavenumber_eq28", "model.py"))
_kb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kb)


def _alphas(lam, kb):
    """Eq. 2.6a, m = 1..4 (complex in general)."""
    out = []
    for m in (1, 2, 3, 4):
        s = 1.0 if 5 - 2 * m > 0 else -1.0
        root = np.sqrt(complex(kb**2 * (lam**4 - 1) ** 2 - 4 * lam**4))
        inner = 1 + 2 * (1 + 1 / lam**4) * kb**2 - 2 * (-1) ** m * kb / lam**4 * root
        out.append(-0.5 + s / 2 * np.sqrt(complex(inner)))
    return out


class _Field:
    """A field sum_j c_j exp(s_j X2) trig(n_j k X1); trig = sin or cos. Derivatives exact."""

    def __init__(self, terms):
        self.terms = terms  # list of (coef, s, n, kind) kind in {"s", "c"}

    def d1(self, kb):
        return _Field([(c * (n * kb) * (1 if kd == "s" else -1), s, n, "c" if kd == "s" else "s")
                       for c, s, n, kd in self.terms if n != 0])

    def d2(self):
        return _Field([(c * s, s, n, kd) for c, s, n, kd in self.terms])

    def __add__(self, other):
        return _Field(self.terms + other.terms)

    def scale(self, f):
        return _Field([(c * f, s, n, kd) for c, s, n, kd in self.terms])

    def ev(self, x1, x2, kb):
        out = np.zeros(np.broadcast(x1, x2).shape, dtype=complex)
        for c, s, n, kd in self.terms:
            tr = np.sin(n * kb * x1) if kd == "s" else np.cos(n * kb * x1)
            out = out + c * np.exp(s * x2) * tr
        return out


def _mul(f, g):
    """Product of two fields, reduced to sums of sin/cos of (n1 +- n2)."""
    terms = []
    for c1, s1, n1, k1 in f.terms:
        for c2, s2, n2, k2 in g.terms:
            c, s = c1 * c2, s1 + s2
            a, b = n1 + n2, n1 - n2
            if k1 == "s" and k2 == "s":
                terms += [(c / 2, s, b, "c"), (-c / 2, s, a, "c")]
            elif k1 == "c" and k2 == "c":
                terms += [(c / 2, s, b, "c"), (c / 2, s, a, "c")]
            elif k1 == "s" and k2 == "c":
                terms += [(c / 2, s, a, "s"), (c / 2, s, b, "s")]
            else:
                terms += [(c / 2, s, a, "s"), (-c / 2, s, b, "s")]
    out = []
    for c, s, n, kd in terms:
        if n < 0:
            n = -n
            if kd == "s":
                c = -c
        if n == 0 and kd == "s":
            continue
        out.append((c, s, n, kd))
    return _Field(out)


def energy_variation(eps, pressure_factor=1.0, n_colloc=60, n_x1=64, seed=0):
    """delta phi^b / zeta^4 (Q0 = a = 1) at the bifurcation point of strain eps on Eq. 2.8.
    pressure_factor multiplies the p(2) term of Eq. 2.12b (1 as printed)."""
    from scipy.integrate import quad

    lam = 1.0 - eps
    kb = _kb.run({"eps": eps}, {})["kbar"]
    al = _alphas(lam, kb)
    a1, a2 = al[0], al[1]
    Om = [lam**2 * (x**3 + x**2 - kb**2 * x + kb**2 / lam**4) for x in (a1, a2)]
    C1 = -1 / kb * (lam**4 * a2**2 + kb**2) / (lam**4 * (a2**2 - a1**2))
    C2 = -(lam**4 * a1**2 + kb**2) / (lam**4 * a2**2 + kb**2) * C1
    C, A = [C1, C2], [a1, a2]
    # first order, Eq. 2.5 (Q = exp(X2) multiplies p)
    psi1 = _Field([(lam * C[m], A[m], 1, "s") for m in range(2)])  # Eq. A 4
    u1 = _Field([(lam**2 * C[m] * A[m], A[m], 1, "s") for m in range(2)])
    u2 = _Field([(-kb * C[m], A[m], 1, "c") for m in range(2)])
    p1 = _Field([(-lam / kb * C[m] * Om[m], A[m] + 1, 1, "c") for m in range(2)])
    p0 = _Field([(1 / lam**2, 1.0, 0, "c")])
    Q = _Field([(1.0, 1.0, 0, "c")])
    # second order: Eqs. A 6, A 8, A 9a, with unknown coefficients
    b = _alphas(lam, 2 * kb)[:2]
    exps = [b[0], b[1], 2 * a1, 2 * a2, a1 + a2]
    Phi = _mul(psi1.d1(kb), psi1.d2().d2()).scale(-lam)
    Theta = _mul(psi1.d1(kb), psi1.d1(kb).d2()).scale(1 / lam)
    basis_psi = [_Field([(lam, e, 2, "s")]) for e in exps]
    basis_p_cos = [_Field([(1.0, e + 1, 2, "c")]) for e in exps]
    basis_p_0 = [_Field([(1.0, e + 1, 0, "c")]) for e in exps]
    nunk = 15

    def grads(ux, uy):
        return [[ux.d1(kb), ux.d2()], [uy.d1(kb), uy.d2()]]

    H1 = grads(u1, u2)

    def residual_parts(v1, v2, p2, fo=False):
        """Second-order equilibrium (div P) and traction P_i2 at X2 = 0, P = Q F - p cof F,
        F = diag(lam, 1/lam) + z H1 + z^2 H2, p = p0 + z p1 + z^2 p2; returns z^2 parts.
        fo: include the product of the first-order fields (p1 cof H1)."""
        H2 = grads(v1, v2)

        def cof(H):
            return [[H[1][1], H[1][0].scale(-1)], [H[0][1].scale(-1), H[0][0]]]

        c1, c2 = cof(H1), cof(H2)
        cof0 = [[1 / lam, 0.0], [0.0, lam]]
        P = [[None, None], [None, None]]
        for i in range(2):
            for j in range(2):
                f = _mul(Q, H2[i][j]) + _mul(p0, c2[i][j]).scale(-1)
                if fo:
                    f = f + _mul(p1, c1[i][j]).scale(-1)
                if p2 is not None and cof0[i][j] != 0.0:
                    f = f + p2.scale(-cof0[i][j])
                P[i][j] = f
        div = [P[i][0].d1(kb) + P[i][1].d2() for i in range(2)]
        trac = [P[i][1] for i in range(2)]
        return div, trac

    rng = np.random.default_rng(seed)
    period = 2 * math.pi / kb
    smin = min(e.real for e in exps)
    depth = 8.0 / (smin + 1.0)
    xs = rng.uniform(0, period, n_colloc)
    ys = -rng.uniform(0, depth, n_colloc)
    w = np.exp(-(smin + 1.0) * ys)
    xb = rng.uniform(0, period, n_colloc // 2)
    zero = _Field([])

    def system_cols(v1, v2, p2, fo=False):
        div, trac = residual_parts(v1, v2, p2, fo)
        return np.concatenate([div[0].ev(xs, ys, kb) * w, div[1].ev(xs, ys, kb) * w,
                               trac[0].ev(xb, 0.0, kb), trac[1].ev(xb, 0.0, kb)])

    # residual = const + sum_j x_j col_j (linear in the unknowns)
    const = system_cols(Phi, Theta, None, fo=True)
    cols = [system_cols(bp.d2().scale(lam), bp.d1(kb).scale(-1 / lam), None) for bp in basis_psi]
    cols += [system_cols(zero, zero, bp) for bp in basis_p_cos + basis_p_0]
    M = np.array(cols).T
    sol = np.linalg.lstsq(M, -const, rcond=None)[0]
    if np.abs(M @ sol + const).max() > 1e-6 * max(1.0, np.abs(const).max()):
        raise RuntimeError("second-order equations not satisfied")
    psi2 = _Field([])
    for j in range(5):
        psi2 = psi2 + basis_psi[j].scale(sol[j])
    v1 = Phi + psi2.d2().scale(lam)
    v2 = Theta + psi2.d1(kb).scale(-1 / lam)
    p2 = _Field([])
    for j in range(5):
        p2 = p2 + basis_p_cos[j].scale(sol[5 + j]) + basis_p_0[j].scale(sol[10 + j])
    H2 = grads(v1, v2)
    x1 = np.arange(n_x1) * period / n_x1

    def integrand(y):
        g1 = [[H1[i][j].ev(x1, y, kb).real for j in range(2)] for i in range(2)]
        g2 = [[H2[i][j].ev(x1, y, kb).real for j in range(2)] for i in range(2)]
        P1 = p1.ev(x1, y, kb).real
        P2 = p2.ev(x1, y, kb).real
        q = math.exp(y)
        alt = (g1[0][0] * g2[1][1] - g1[0][1] * g2[1][0]) + (g2[0][0] * g1[1][1] - g2[0][1] * g1[1][0])
        det1 = g1[0][0] * g1[1][1] - g1[0][1] * g1[1][0]
        det2 = g2[0][0] * g2[1][1] - g2[0][1] * g2[1][0]
        t3 = -2.0 * (P1 * alt + P2 * det1)  # Eq. 2.12a
        hh = sum(g2[i][j] ** 2 for i in range(2) for j in range(2))
        t4 = q * (hh - 2.0 / lam**2 * det2) - pressure_factor * P2 * (g2[0][0] / lam + lam * g2[1][1])  # Eq. 2.12b
        return (t3 + t4).mean() * period

    val = quad(integrand, -np.inf, 0.0, limit=400)[0]
    return 0.5 * val  # Eq. 2.11


def m_point(settings, pressure_factor):
    from scipy.optimize import brentq

    lo, hi, n = settings["eps_scan_lo"], settings["eps_scan_hi"], int(settings["n_scan"])
    grid = np.linspace(lo, hi, n)
    kw = {"n_colloc": int(settings["n_colloc"]), "n_x1": int(settings["n_x1"])}
    prev = None
    for e in grid:
        v = energy_variation(float(e), pressure_factor, **kw)
        if prev is not None and prev[1] > 0 >= v:
            r = brentq(lambda x: energy_variation(x, pressure_factor, **kw), prev[0], float(e), xtol=1e-6)
            return {"eps_M": r, "kbar_M": _kb.run({"eps": r}, {})["kbar"]}
        prev = (float(e), v)
    # no change of sign from + to - in the scan: the wrinkle stays stable up to the end of the
    # bifurcation curve, the Biot strain, where kbar diverges (the denominator of Eq. 2.8 vanishes)
    lam_b = brentq(lambda x: x**3 + x**2 + x - 1, 0.1, 0.99, xtol=1e-14)
    return {"eps_M": 1.0 - lam_b, "kbar_M": float("inf")}


def run(inputs, settings):
    return {"eps_M": m_point(settings, 1.0)["eps_M"]}
