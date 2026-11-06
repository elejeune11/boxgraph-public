# 1D blood-flow network: Eqs. (2), (3) with the algebraic law (9)-(10), alpha = 1, Pext = 0,
# K_R = 8 pi nu, solved by the second-order Taylor-Galerkin scheme (22)-(23) with P1 elements and
# a consistent mass matrix, first-order characteristic extrapolation at the vessel ends
# (Section 2.3), and interfaces/junctions solved by Newton iteration (tolerance on the relative
# increment): mass conservation (27)/(35), total-pressure relations with the angle losses
# (36)-(37) (zero losses: (32)/(38)), and the outgoing characteristic variables (18)-(19).
#
# This model: the three-vessel bifurcation of Section 3.1 (Figs. 6-8), returning A, W1, W2 at
# the midpoint of each vessel at time t. The Network class is also used by the endograft model.
# Ports in CGS units: cm, s, g, dyne.
import math

import numpy as np
from scipy.linalg import solve_banded


class Network:
    """vessels: list of dicts (L, n, R0, E); h0, rho, nu shared. inlet: vessel index fed at z = 0;
    links: (parent, [daughters], (gamma_1, [(gamma_i, angle_i)])); outlets: vessels with a
    non-reflecting distal end. inlet_kind: 'pressure' (P(t) imposed, W2 extrapolated) or
    'characteristic' (W1 = g1(t) of Eq. (25), the forward characteristic of the pulse)."""

    def __init__(self, vessels, h0, rho, nu, inlet, links, outlets, pulse, tol, inlet_kind):
        self.rho = rho
        self.KR = 8.0 * math.pi * nu
        self.inlet, self.links, self.outlets = inlet, links, outlets
        self.pulse, self.tol, self.inlet_kind = pulse, tol, inlet_kind
        self.ves = []
        off = 0
        kn, cFn, b2n, hn = [], [], [], []
        for v in vessels:
            n = int(v["n"])
            A0 = math.pi * v["R0"] ** 2
            beta = v["E"] * h0 * math.sqrt(math.pi)                 # Eq. (10)
            k = math.sqrt(beta / (2.0 * rho * A0))
            d = dict(n=n, h=v["L"] / n, A0=A0, beta=beta, k=k, first=off, last=off + n, mid=off + n // 2)
            self.ves.append(d)
            kn += [k] * (n + 1)
            cFn += [beta / (3.0 * rho * A0)] * (n + 1)
            b2n += [beta / (2.0 * rho * A0)] * (n + 1)
            hn += [d["h"]] * (n + 1)
            off += n + 1
        N = off
        self.k = np.array(kn)
        self.cF = np.array(cFn)
        self.b2 = np.array(b2n)
        hn = np.array(hn)
        self.A = np.concatenate([np.full(d["n"] + 1, d["A0"]) for d in self.ves])
        self.Q = np.zeros(N)
        ends = np.zeros(N, bool)
        for d in self.ves:
            ends[d["first"]] = ends[d["last"]] = True
        self.ends = ends
        self.I = np.flatnonzero(~ends)                     # interior nodes
        self.eL = np.flatnonzero(~np.isin(np.arange(N), [d["last"] for d in self.ves]))  # element j = (j, j+1)
        epos = -np.ones(N, int)
        epos[self.eL] = np.arange(len(self.eL))
        self.el = epos[self.I - 1]                         # element left of each interior node
        self.er = epos[self.I]                             # element right of each interior node
        self.hI = hn[self.I]
        self.he = hn[self.eL]
        m = len(self.I)
        ab = np.zeros((3, m))
        ab[1] = 4.0 * self.hI / 6.0
        same = (self.I[1:] - self.I[:-1]) == 1
        ab[0, 1:] = np.where(same, self.hI[1:] / 6.0, 0.0)
        ab[2, :-1] = np.where(same, self.hI[:-1] / 6.0, 0.0)
        self.ab = ab
        self.endL = ends[self.I - 1]
        self.endR = ends[self.I + 1]
        self.W2rest = [-4.0 * d["k"] * d["A0"] ** 0.25 for d in self.ves]

    # vessel-level helpers
    def Pd(self, d, A):
        return d["beta"] * (math.sqrt(A) - math.sqrt(d["A0"])) / d["A0"]           # Eq. (9)

    def A_of_P(self, d, P):
        return (math.sqrt(d["A0"]) + P * d["A0"] / d["beta"]) ** 2

    def from_W(self, d, W1, W2):                                                 # Eq. (19)
        A = ((W1 - W2) / (8.0 * d["k"])) ** 4
        return A, A * (W1 + W2) / 2.0

    def _W(self, j, k):
        A, Q = self.A[j], self.Q[j]
        c = k * A ** 0.25
        return Q / A, c

    def extrap(self, d, which, dt):
        """Outgoing characteristic at t^{n+1}: W at the foot of the characteristic (linear in the end element)."""
        k, h = d["k"], d["h"]
        if which == 1:
            j0, j1 = d["last"], d["last"] - 1
            sgn = 1.0
        else:
            j0, j1 = d["first"], d["first"] + 1
            sgn = -1.0
        u0, c0 = self._W(j0, k)
        u1, c1 = self._W(j1, k)
        w0, w1 = u0 + sgn * 4.0 * c0, u1 + sgn * 4.0 * c1
        lam = u0 + sgn * c0
        x = abs(lam) * dt / h
        return w0 + (w1 - w0) * x

    def junction(self, p, ds, losses, dt):
        P = self.ves[p]
        D = [self.ves[i] for i in ds]
        g1, gd = losses
        W1p = self.extrap(P, 1, dt)
        W2d = [self.extrap(d, 2, dt) for d in D]
        s = [math.sqrt(2.0 * (1.0 - math.cos(a))) for _, a in gd]
        g = [gi for gi, _ in gd]
        x = [self.A[P["last"]], self.Q[P["last"]]]
        for d in D:
            x += [self.A[d["first"]], self.Q[d["first"]]]
        x = np.array(x)
        nd = len(D)
        nx = 2 + 2 * nd
        sc = np.array([v["A0"] if j == 0 else v["A0"] * v["k"] for v in [P] + D for j in (0, 1)])
        kp2 = P["k"] ** 2
        rho = self.rho
        for _ in range(50):
            f = np.zeros(nx)
            J = np.zeros((nx, nx))
            Ap, Qp = x[0], x[1]
            up = Qp / Ap
            f[0] = up + 4.0 * P["k"] * Ap ** 0.25 - W1p
            J[0, 0] = -up / Ap + P["k"] * Ap ** -0.75
            J[0, 1] = 1.0 / Ap
            f[1] = Qp - sum(x[3 + 2 * i] for i in range(nd))
            J[1, 1] = 1.0
            ptp = self.Pd(P, Ap) / rho + 0.5 * up * up - g1 * up * abs(up)
            dptp_dA = P["beta"] / (2.0 * rho * P["A0"] * math.sqrt(Ap)) - up * up / Ap + 2.0 * g1 * up * abs(up) / Ap
            dptp_dQ = up / Ap - 2.0 * g1 * abs(up) / Ap
            for i, d in enumerate(D):
                ia, iq = 2 + 2 * i, 3 + 2 * i
                Ad, Qd = x[ia], x[iq]
                ud = Qd / Ad
                J[1, iq] = -1.0
                r = 2 + 2 * i
                f[r] = ud - 4.0 * d["k"] * Ad ** 0.25 - W2d[i]
                J[r, ia] = -ud / Ad - d["k"] * Ad ** -0.75
                J[r, iq] = 1.0 / Ad
                gs = g[i] * s[i]
                ptd = self.Pd(d, Ad) / rho + 0.5 * ud * ud + gs * ud * abs(ud)
                r = 3 + 2 * i
                f[r] = (ptp - ptd) / kp2
                J[r, 0] = dptp_dA / kp2
                J[r, 1] = dptp_dQ / kp2
                J[r, ia] = -(d["beta"] / (2.0 * rho * d["A0"] * math.sqrt(Ad)) - ud * ud / Ad
                             - 2.0 * gs * ud * abs(ud) / Ad) / kp2
                J[r, iq] = -(ud / Ad + 2.0 * gs * abs(ud) / Ad) / kp2
            dx = np.linalg.solve(J, -f)
            x = x + dx
            if np.max(np.abs(dx) / sc) < self.tol:
                break
        return x

    def step(self, t, dt):
        A, Q = self.A, self.Q
        bA, bQ = {}, {}
        # inlet
        d = self.ves[self.inlet]
        W2 = self.extrap(d, 2, dt)
        Pin = self.pulse(t + dt)
        if self.inlet_kind == "pressure":
            Ai = self.A_of_P(d, Pin)
            bA[d["first"]], bQ[d["first"]] = Ai, Ai * (W2 + 4.0 * d["k"] * Ai ** 0.25)
        else:
            g1 = self.W2rest[self.inlet] + 8.0 * d["k"] * self.A_of_P(d, Pin) ** 0.25
            bA[d["first"]], bQ[d["first"]] = self.from_W(d, g1, W2)
        # outlets: incoming W2 held at its rest value; W1 extrapolated
        for i in self.outlets:
            d = self.ves[i]
            bA[d["last"]], bQ[d["last"]] = self.from_W(d, self.extrap(d, 1, dt), self.W2rest[i])
        for p, ds, losses in self.links:
            x = self.junction(p, ds, losses, dt)
            bA[self.ves[p]["last"]], bQ[self.ves[p]["last"]] = x[0], x[1]
            for i, di in enumerate(ds):
                bA[self.ves[di]["first"]], bQ[self.ves[di]["first"]] = x[2 + 2 * i], x[3 + 2 * i]
        # interior: Taylor-Galerkin (23)
        KR = self.KR
        FQ = Q * Q / A + self.cF * A ** 1.5
        BQ = -KR * Q / A
        FLW_A = Q + 0.5 * dt * BQ
        FLW_Q = FQ + dt * (Q / A) * BQ
        BLW_Q = BQ - 0.5 * dt * KR / A * BQ
        a, b = self.eL, self.eL + 1
        Am = 0.5 * (A[a] + A[b])
        Qm = 0.5 * (Q[a] + Q[b])
        dFA = Q[b] - Q[a]
        dFQ = FQ[b] - FQ[a]
        H21 = -Qm * Qm / (Am * Am) + self.b2[a] * np.sqrt(Am)
        HdF_A = dFQ
        HdF_Q = H21 * dFA + (2.0 * Qm / Am) * dFQ
        BUdF_Q = (KR * Qm / (Am * Am)) * dFA - (KR / Am) * dFQ
        I, el, er, h = self.I, self.el, self.er, self.hI

        def mass(v):
            return h / 6.0 * (v[I - 1] + 4.0 * v[I] + v[I + 1])

        rA = mass(A) + 0.5 * dt * (FLW_A[I - 1] - FLW_A[I + 1]) - 0.5 * dt * dt * (HdF_A[el] - HdF_A[er]) / h
        rQ = (mass(Q) + 0.5 * dt * (FLW_Q[I - 1] - FLW_Q[I + 1])
              - 0.25 * dt * dt * (BUdF_Q[el] + BUdF_Q[er])
              - 0.5 * dt * dt * (HdF_Q[el] - HdF_Q[er]) / h
              + dt * mass(BLW_Q))
        An = A.copy()
        Qn = Q.copy()
        for j in bA:
            An[j], Qn[j] = bA[j], bQ[j]
        rA -= h / 6.0 * (np.where(self.endL, An[I - 1], 0.0) + np.where(self.endR, An[I + 1], 0.0))
        rQ -= h / 6.0 * (np.where(self.endL, Qn[I - 1], 0.0) + np.where(self.endR, Qn[I + 1], 0.0))
        sol = solve_banded((1, 1), self.ab, np.column_stack([rA, rQ]))
        An[I] = sol[:, 0]
        Qn[I] = sol[:, 1]
        self.A, self.Q = An, Qn


def simulate(net, dt, t_end, probes):
    """A, W1, W2 at the midpoint of each probed vessel, every time step."""
    n = int(round(t_end / dt))
    idx = []
    for i in probes:
        d = net.ves[i]
        idx.append((d["mid"], d["mid"] + (d["n"] % 2)))
    j0 = np.array([a for a, _ in idx])
    j1 = np.array([b for _, b in idx])
    kk = np.array([net.ves[i]["k"] for i in probes])
    RA = np.empty((n + 1, len(probes)))
    RQ = np.empty((n + 1, len(probes)))
    RA[0] = 0.5 * (net.A[j0] + net.A[j1])
    RQ[0] = 0.5 * (net.Q[j0] + net.Q[j1])
    for s in range(n):
        net.step(s * dt, dt)
        RA[s + 1] = 0.5 * (net.A[j0] + net.A[j1])
        RQ[s + 1] = 0.5 * (net.Q[j0] + net.Q[j1])
        if not (np.all(np.isfinite(RA[s + 1])) and np.all(RA[s + 1] > 0)):
            RA[s + 1:] = np.nan
            RQ[s + 1:] = np.nan
            break
    u = RQ / RA
    c4 = 4.0 * kk * RA ** 0.25
    out = np.empty((n + 1, 3 * len(probes)))
    out[:, 0::3] = RA
    out[:, 1::3] = u + c4
    out[:, 2::3] = u - c4
    return out


def half_sine(amp, T):
    def p(t):
        return amp * math.sin(math.pi * t / T) if 0.0 <= t <= T else 0.0
    return p


def at_time(rec, dt, t):
    j = t / dt
    i = int(math.floor(j + 1e-9))
    if i < 0 or i >= len(rec):
        return [float("nan")] * rec.shape[1]
    if i == len(rec) - 1:
        return list(rec[i])
    w = max(j - i, 0.0)
    return list((1 - w) * rec[i] + w * rec[i + 1])


_MEMO = {}
NAMES = ("A_1", "W1_1", "W2_1", "A_2", "W1_2", "W2_2", "A_3", "W1_3", "W2_3")


def check_alpha(alpha):
    # the scheme uses the characteristic variables (18)-(19), which the paper gives for alpha = 1
    if abs(alpha - 1.0) > 1e-12:
        raise ValueError("this solver implements alpha = 1 only (Eqs. 18-19)")


def _simulate(inp, settings):
    check_alpha(inp["alpha"])
    n = int(settings["n_elements"])
    vs = [dict(L=inp["L"], n=n, R0=inp[f"R0_{i}"], E=inp["E"]) for i in (1, 2, 3)]
    losses = (inp["gamma_1"], [(inp["gamma_2"], inp["alpha_2"]), (inp["gamma_3"], inp["alpha_3"])])
    net = Network(vs, inp["h0"], inp["rho"], inp["nu"], 0, [(0, [1, 2], losses)], [1, 2],
                  half_sine(inp["P_amp"], inp["T_pulse"]), float(settings["newton_tol"]),
                  str(settings["inlet"]))
    return simulate(net, float(settings["dt"]), float(settings["t_end"]), [0, 1, 2])


def run(inputs, settings):
    base = {k: float(v) for k, v in inputs.items() if k != "t"}
    key = (tuple(sorted(base.items())), tuple(sorted((k, str(v)) for k, v in settings.items())))
    if key not in _MEMO:
        _MEMO.clear()
        _MEMO[key] = _simulate(base, settings)
    vals = at_time(_MEMO[key], float(settings["dt"]), float(inputs["t"]))
    return dict(zip(NAMES, vals))
