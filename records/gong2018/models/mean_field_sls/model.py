"""Mean-field ("ensemble clutch") motor-clutch model on a viscoelastic substrate.

Eqs. S3-S8 (SI pp. 11-12) with the substrate as parallel Maxwell elements
(Eq. 2 / S4 for one element; Eqs. S11-S12 for several) and the clutch
reinforcement rule of the main text (p. 3) and SI p. 11.

Units: pN, nm, s.  Port units are the declared ones.

State of one formation-breakage cycle: Pb (fraction engaged), xc (filament end
of the ensemble clutch), x_eta_i (dashpot displacement of Maxwell element i).
The substrate end xs is algebraic (force balance of the clutch spring
K = kc nc Pb against the substrate):
    K (xc - xs) = kl xs + sum_i ka_i (xs - x_eta_i)
    eta_i dx_eta_i/dt = ka_i (xs - x_eta_i)                      (S11)
    dPb/dt = (1 - Pb) ron - Pb roff0 exp(Fc/Fb),  Fc = kc (xc - xs)   (S3)
    dxc/dt = vu (1 - Fs/(nm Fm)),  Fs = K (xc - xs)              (S6, S7)
A cycle starts with every clutch free and the substrate at rest, and ends when
Pb falls below `break_fraction` (reader's choice: the paper says only "all
clutches break") after it has peaked.  Vf = xc / t_total (S8), Vs = Vp - Vf.

Reinforcement (p. 3; SI p. 11): Fa is the time average of the clutch force Fc
over a cycle; if Fa > Fcr the next cycle uses ron = ron0 (1 + alpha (Fa - Fcr)).
`n_cycles` cycles are run (the paper: "at least 10 life cycles") and the
reported speed is that of the last cycle.  A cycle that has not ended by
`t_max` is a stable ("divergent") adhesion; its speed is xc/t_max.
"""
import math

import numpy as np
from scipy.integrate import solve_ivp


def _xs(K, xc, kl, ka, xeta):
    return (K * xc + float(np.dot(ka, xeta))) / (K + kl + float(np.sum(ka)))


def cycle(p, ka, eta, kl, ron, settings):
    """One formation-breakage cycle. Returns (Vf, Fa, t_total, ended)."""
    kc, nc, nm, Fm, vu = p["kc"], p["nc"], p["nm"], p["Fm"], p["vu"]
    Fb, roff0 = p["Fb"], p["roff0"]
    # a Maxwell element with ka = 0 carries no force and is left out
    keep = [i for i in range(len(ka)) if ka[i] > 0]
    ka = np.asarray([ka[i] for i in keep], float)
    eta = np.asarray([eta[i] for i in keep], float)
    n = len(ka)
    thr = settings["break_fraction"]
    t_max = settings["t_max"]

    # Pb is integrated as u = ln Pb (Pb > 0 always; the final rupture cascade,
    # where roff grows by many orders of magnitude, stays smooth in u).
    def forces(y):
        u, xc, xeta = y[0], y[1], y[2:2 + n]
        u = min(max(u, -700.0), 5.0)   # guards against overflow only
        Pb = math.exp(u)
        K = kc * nc * Pb
        xs = _xs(K, xc, kl, ka, xeta)
        return u, Pb, xs, kc * (xc - xs), K * (xc - xs)

    def rhs(t, y):
        u, Pb, xs, Fc, Fs = forces(y)
        # capped at e^50: beyond that the clutch is gone within any step taken
        roff = roff0 * math.exp(min(Fc / Fb, 50.0))
        du = (1.0 - Pb) * ron * math.exp(-u) - roff
        dxc = vu * (1.0 - Fs / (nm * Fm))
        dxeta = ka * (xs - y[2:2 + n]) / eta if n else np.zeros(0)
        return np.concatenate(([du, dxc], dxeta))

    # the event fires when Pb crosses thr downward; Pb starts near 0 and rises
    # through thr upward first, which the direction filter skips.
    lthr = math.log(thr)

    def broken(t, y):
        return y[0] - lthr
    broken.terminal = True
    broken.direction = -1

    y0 = np.zeros(n + 2)
    y0[0] = math.log(settings["p_start"])
    sol = solve_ivp(rhs, (0.0, t_max), y0, method="Radau", events=broken,
                    rtol=settings["rtol"], atol=settings["rtol"],
                    max_step=settings["max_step"], dense_output=True)
    t_end = sol.t[-1]
    ended = sol.status == 1
    if sol.status < 0:
        # The rupture cascade is a finite-time collapse: as Pb falls the
        # substrate unloads, the clutch stretch jumps and roff runs away, and
        # the step size the solver needs goes to zero.  If that is where it
        # stopped (dissociation outrunning binding by a large factor), the
        # cycle has ended there; otherwise it is a genuine failure.
        d = rhs(t_end, sol.y[:, -1])
        if d[0] > -1e3 * ron:
            raise RuntimeError(f"ODE solver failed at t = {t_end}: {sol.message}")
        ended = True
    xc = sol.y[1, -1]
    # Fa: time average of the clutch force over the cycle, by the trapezoid
    # rule on the solver's steps refined with its dense output
    ts = np.union1d(sol.t, np.linspace(0.0, t_end, int(settings["n_avg"]) + 1))
    ys = sol.sol(ts) if sol.sol is not None else sol.y
    if sol.sol is None:
        ts = sol.t
    fs = np.array([forces(ys[:, j]) for j in range(len(ts))])
    fc, w = fs[:, 3], (fs[:, 1] if settings["fa_weighted"] else np.ones(len(ts)))

    def integral(v):
        return float(np.sum(0.5 * (v[1:] + v[:-1]) * np.diff(ts)))
    Fa = integral(fc * w) / integral(w)
    return xc / t_end, Fa, t_end, ended


def mean_speed(p, ka, eta, kl, settings):
    ron0, alpha, Fcr = p["ron0"], p["alpha"], p["Fcr"]
    ron = ron0
    Vf = Fa = t_end = None
    ended = True
    for _ in range(int(settings["n_cycles"])):
        Vf, Fa, t_end, ended = cycle(p, ka, eta, kl, ron, settings)
        base = ron if settings["cumulative"] else ron0
        ron = base * (1.0 + alpha * (Fa - Fcr)) if Fa > Fcr else base
    return {"Vs": p["Vp"] - Vf, "Vf": Vf, "t_life": t_end, "Fa": Fa}


PARAMS = ("nm", "Fm", "Fcr", "nc", "Fb", "ron0", "roff0", "kc", "vu", "Vp", "alpha")


def run(inputs, settings):
    p = {k: inputs[k] for k in PARAMS}
    out = mean_speed(p, [inputs["ka"]], [inputs["eta"]], inputs["kl"], settings)
    return {"Vs": out["Vs"], "t_life": out["t_life"], "Fa": out["Fa"]}
