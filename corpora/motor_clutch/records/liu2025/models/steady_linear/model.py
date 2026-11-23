"""Steady state of the linear molecular-clutch model (Methods, Eqs. 1, 4, 5/11, 8, 9, 10).

Units of the ports: E Pa, r and ly and l nm, kc pN/nm, kT pN*nm, xt nm, rates 1/s,
v and v0 nm/s, Fst pN, densities 1/um^2 (so P in pN/um^2 = Pa), R nm, S um^2.

Eq. 1:  k's = 4 pi r E / 9           (Pa * nm = 1e-6 pN/nm)
Eq. 5:  k = kc k's / (kc + k's)
Eq. 11: F(l) = k l for l <= ly, k ly otherwise
Eq. 4:  koff(F) = k0off exp(beta xt |F|) + k0'off exp(beta x't |F|),  beta = 1/kT
Eq. 9:  pon(l) = kon exp(-(1/v) I(l)) / (v + kon int_0^inf exp(-(1/v) I(l')) dl'),  I(l) = int_0^l koff
Eq. 8:  sigma_c int F pon dl = sigma_m Fst (1 - v/v0)          (Fc = Nc ..., Nc = sigma_c S, Nm = sigma_m S)
Eq. 10: P = Fc / S = sigma_c int F pon dl
Eq. 8, line 5: xs = Fc / ks,  ks = 4 pi R E / 9 (Methods text), Fc = P S

The steady states are the roots of g(v) = P_c(v) - P_m(v), P_m = sigma_m Fst (1 - v/v0).
Stable roots: g'(v) > 0 (Extended Data Fig. 1(a): above the root the clutches hold more than the
motors pull, so the flow slows back). Beyond ly the off-rate is constant, so the tail integrals
are closed-form.
"""
import math

import numpy as np

PA_NM_TO_PN_PER_NM = 1e-6  # 1 Pa * 1 nm = 1e-12 N/m = 1e-6 pN/nm


def spring(p):
    ksp = 4.0 * math.pi * p["r"] * p["E"] * PA_NM_TO_PN_PER_NM / 9.0
    return p["kc"] * ksp / (p["kc"] + ksp)


def koff_of_F(F, p):
    a = np.minimum(p["xt"] * np.abs(F) / p["kT"], 700.0)
    b = np.minimum(p["xtp"] * np.abs(F) / p["kT"], 700.0)
    return p["k0off"] * np.exp(a) + p["k0offp"] * np.exp(b)


def _cumI(l, p, k, ly):
    ko = koff_of_F(k * np.minimum(l, ly), p)
    return np.concatenate([[0.0], np.cumsum(0.5 * (ko[1:] + ko[:-1]) * np.diff(l))])


def traction_per_site(v, p, nl=8000):
    """Fc/Nc at a given flow speed v (pN): Eq. 6 with Eq. 9, without the force balance.
    p may give the clutch spring constant k directly instead of E, r, kc."""
    g = Grid(p, max(v, 1e-12), n=nl)
    Z, M = g.moments(v)
    return float(p["kon"] * M[0] / (v + p["kon"] * Z[0]))


class Grid:
    """The extension grid for one E, independent of v: I(l) and F(l) on [0, lend], where lend
    is ly or, if sooner, where exp(-I/v0) < exp(-depth) (nothing bound beyond, at any v <= v0).
    Nodes are packed towards l = 0 (l = lend u^2) so slow flows are resolved too. If lend = ly,
    the off-rate is constant beyond it and the tail integrals are closed-form."""

    def __init__(self, p, v_max, n=8000, depth=60.0):
        self.k = k = p["k"] if "k" in p else spring(p)
        ly = p["ly"]
        lend = 10.0
        while True:  # double until deep enough or at ly
            if lend >= ly:
                lend = ly
                break
            l = np.linspace(0.0, lend, 2000)
            if _cumI(l, p, k, ly)[-1] / v_max > depth or lend > 1e12:
                break
            lend *= 2.0
        u = np.linspace(0.0, 1.0, n)
        l = lend * u * u
        I = _cumI(l, p, k, ly)
        self.l, self.I, self.F = l, I, k * np.minimum(l, ly)
        self.capped = lend >= ly
        self.c_tail = float(koff_of_F(k * ly, p)) if self.capped else None
        self.F_tail = k * ly if self.capped else None

    def moments(self, v):
        """For flow speeds v (array): Z = int S dl, M = int F S dl, with S = exp(-I/v)."""
        v = np.atleast_1d(np.asarray(v, float))[:, None]
        S = np.exp(-self.I[None, :] / v)
        dl = np.diff(self.l)
        Z = np.sum(0.5 * (S[:, 1:] + S[:, :-1]) * dl, axis=1)
        FS = self.F[None, :] * S
        M = np.sum(0.5 * (FS[:, 1:] + FS[:, :-1]) * dl, axis=1)
        if self.capped:
            tail = S[:, -1] * v[:, 0] / self.c_tail
            Z = Z + tail
            M = M + self.F_tail * tail
        return Z, M


def traction_clutch(v, grid, p):
    """P_c(v) = sigma_c int F pon dl (Pa), the bound fraction int pon dl, and Z, M."""
    v = np.atleast_1d(np.asarray(v, float))
    Z, M = grid.moments(v)
    denom = v + p["kon"] * Z
    return p["sc"] * p["kon"] * M / denom, p["kon"] * Z / denom


def steady_states(p, nv=600, nl=8000):
    """All roots of g(v) on (1e-5 v0, v0), with stability. Returns a list of dicts sorted by v."""
    v0 = p["v0"]
    vs = v0 * np.logspace(-5, 0, nv)[:-1]
    vs = np.concatenate([vs, [v0 * (1 - 1e-9)]])
    grid = Grid(p, v0, n=nl)
    Pc, _ = traction_clutch(vs, grid, p)
    g = Pc - p["sm"] * p["Fst"] * (1 - vs / v0)
    roots = []
    for i in np.where(np.sign(g[:-1]) * np.sign(g[1:]) < 0)[0]:
        a, b, ga, gb = vs[i], vs[i + 1], g[i], g[i + 1]
        for _ in range(80):  # bisection on log v
            m = math.sqrt(a * b)
            gm = traction_clutch(m, grid, p)[0][0] - p["sm"] * p["Fst"] * (1 - m / v0)
            if np.sign(gm) == np.sign(ga):
                a, ga = m, gm
            else:
                b, gb = m, gm
            if b / a - 1 < 1e-10:
                break
        v = math.sqrt(a * b)
        roots.append({"v": v, "stable": bool(gb > ga)})
    return roots, grid


def pick(roots, branch):
    if branch == "unstable":  # the unstable root between two stable ones (bistable region only)
        un = [r for r in roots if not r["stable"]]
        return un[0] if len(roots) == 3 and un else None
    stable = [r for r in roots if r["stable"]]
    if not stable:
        return None
    if branch == "strong":  # low gear: slowest flow, highest traction
        return min(stable, key=lambda r: r["v"])
    if branch == "weak":
        return max(stable, key=lambda r: r["v"])
    raise ValueError(branch)


def params(inputs):
    p = dict(inputs)
    if p.get("ly") is None:
        p["ly"] = math.inf
    return p


def run(inputs, settings):
    p = params(inputs)
    roots, grid = steady_states(p, nv=int(settings.get("n_v", 600)), nl=int(settings.get("n_l", 8000)))
    r = pick(roots, settings.get("branch", "strong"))
    if r is None:
        nan = float("nan")
        return {"P": nan, "v": nan, "n_on": nan, "F1": nan, "xs": nan}
    v = r["v"]
    Pc, bound = traction_clutch(v, grid, p)
    P = float(Pc[0])
    n_on = float(p["sc"] * bound[0])  # engaged clutches per um^2
    F1 = P / n_on  # mean tension per engaged clutch (Appendix E, Eq. E1), pN
    ks = 4.0 * math.pi * p["R"] * p["E"] * PA_NM_TO_PN_PER_NM / 9.0
    xs = P * p["S"] / ks  # Fc = P S (pN), xs in nm
    return {"P": P, "v": float(v), "n_on": n_on, "F1": float(F1), "xs": float(xs)}
