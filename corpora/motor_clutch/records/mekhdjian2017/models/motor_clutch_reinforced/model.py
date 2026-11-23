# Motor-clutch model with force-dependent clutch reinforcement (Supplemental Materials, pp. 24-29):
# Chan and Odde (2008) / Bangasser et al. (2013) rules, Bell slip-bond off-rate, direct Gillespie
# method (Eq. 13), clutch addition at rate kadd* = kadd n_threshold f_available (Eqs. 10-12), the
# substrate spring from the effective Young's modulus (Eq. 5) and the traction stress (Eq. 4).
# Units: nm, pN, s; E in kPa; stress in Pa. Positions and forces positive in the retrograde direction.
import math

import numpy as np


def ksub_from_E(E_kPa, r_nm):
    """Eq. 5 solved for the spring: E = 9 ksub / (4 pi r)  ->  ksub = 4 pi r E / 9.
    kPa * nm = 1e3 N/m^2 * 1e-9 m = 1e-6 N/m = 1e-3 pN/nm."""
    return 4.0 * math.pi * r_nm * E_kPa * 1e-3 / 9.0


def stress_from_force(F_pN, r_nm):
    """Eq. 4: T = F / (pi r^2). pN / nm^2 = 1e-12 N / 1e-18 m^2 = 1e6 Pa."""
    return F_pN / (math.pi * r_nm ** 2) * 1e6


def simulate(inputs, settings):
    nm, Fm, vu = inputs["nm"], inputs["Fm"], inputs["vu"]
    kon, koff, Fb, kc = inputs["kon"], inputs["koff"], inputs["Fb"], inputs["kc"]
    r = inputs["r_adh"]
    ksub = ksub_from_E(inputs["E"], r)
    kadd = inputs.get("kadd", 0.0)
    Fth = inputs.get("Fthresh", math.inf)
    n0 = int(round(inputs["nc"]))
    nmax = int(round(inputs.get("ncmax", n0)))
    nmax = max(nmax, n0)
    n_events = int(settings["n_events"])
    rng = np.random.default_rng(int(settings["seed"]))
    Fstall = nm * Fm

    bound = np.zeros(nmax, dtype=bool)
    x = np.zeros(nmax)       # F-actin end of each clutch, nm
    n = n0                   # current clutch ensemble size, nclutch(t)
    xsub = 0.0
    t = 0.0
    v_int = F_int = n_int = nc_int = 0.0
    U = rng.random((n_events, 2))
    for step in range(n_events):
        b = bound[:n]
        xb = x[:n][b]
        nb = xb.size
        if nb:
            Fb_i = kc * (xb - xsub)
            with np.errstate(over="ignore"):
                kb = koff * np.exp(Fb_i / Fb)
            sum_b = float(kb.sum())
        else:
            sum_b = 0.0
        sum_u = (n - nb) * kon
        # Eqs. 10-12: clutch addition rate
        if kadd > 0.0 and n < nmax and nb:
            n_th = int(np.count_nonzero(Fb_i > Fth))
            k_add = kadd * n_th * (nmax - n) / nmax
        else:
            k_add = 0.0
        total = sum_b + sum_u + k_add
        if not math.isfinite(total) or total <= 0.0:
            break
        # Eq. 13: time to the next event; a second random number selects it
        dt = -math.log(U[step, 0]) / total
        pick = U[step, 1] * total
        if pick < sum_b:
            j = int(np.searchsorted(np.cumsum(kb), pick, side="right"))
            j = min(j, nb - 1)
            idx = np.flatnonzero(b)[j]
            bound[idx] = False
        elif pick < sum_b + sum_u:
            free = np.flatnonzero(~b)
            j = min(int((pick - sum_b) / kon), free.size - 1)
            idx = free[j]
            bound[idx] = True
            x[idx] = xsub
        else:
            # a new clutch joins at the substrate position, unbound
            x[n] = xsub
            bound[n] = False
            n += 1
        # retrograde flow from the substrate force (linear force-velocity), over this interval
        v = vu * (1.0 - ksub * xsub / Fstall)
        v_int += v * dt
        F_int += ksub * xsub * dt
        n_int += nb * dt
        nc_int += n * dt
        t += dt
        bb = bound[:n]
        x[:n][bb] += v * dt
        nb2 = int(bb.sum())
        xsub = kc * float(x[:n][bb].sum()) / (ksub + nb2 * kc) if nb2 else 0.0
    T = t if t > 0 else 1.0
    F_mean = F_int / T
    return {
        "T": stress_from_force(F_mean, r),
        "F_sub": F_mean,
        "v_retro": v_int / T,
        "n_eng": n_int / T,
        "nc_mean": nc_int / T,
        "t_sim": t,
    }


def run(inputs, settings):
    return simulate(inputs, settings)
