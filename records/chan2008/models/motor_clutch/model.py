# Stochastic motor-clutch model on a compliant substrate (SOM Eqs. 1-5).
# Units: nm, pN, s. Sign convention as in Table S1: retrograde motion is
# negative x, so vu, Fm and Fb are negative and clutch tensions are negative.
import numpy as np


def simulate(nm, Fm, vu, nc, kon, koff, Fb, kc, ksub, settings):
    dt = settings["dt"]
    n_steps = int(round(settings["t_total"] / dt))
    rng = np.random.default_rng(settings["seed"])
    n = int(round(nc))
    Fstall = nm * Fm                                   # Eq. 4
    bound = np.zeros(n, dtype=bool)
    x = np.zeros(n)
    xsub = 0.0
    p_on = 1.0 - np.exp(-kon * dt)
    v_sum = 0.0
    trac_sum = 0.0
    trac_min = 0.0
    with np.errstate(over="ignore"):
        for _ in range(n_steps):
            # association: a newly engaged clutch starts unstretched, at xsub
            new = (~bound) & (rng.random(n) < p_on)
            x[new] = xsub
            bound |= new
            # dissociation at the loaded off rate (Eqs. 1-2)
            F = kc * (x - xsub)
            koff_star = koff * np.exp(F / Fb)
            off = bound & (rng.random(n) < 1.0 - np.exp(-koff_star * dt))
            bound &= ~off
            # force balance for the substrate position (Eq. 5)
            neng = int(bound.sum())
            xsub = kc * x[bound].sum() / (ksub + neng * kc) if neng else 0.0
            # linear force-velocity relation of the motors (Eq. 3)
            v = vu * (1.0 - ksub * xsub / Fstall)
            x[bound] += v * dt
            v_sum += v
            trac = ksub * xsub
            trac_sum += trac
            trac_min = min(trac_min, trac)
    return {
        "v_retro": -v_sum / n_steps,     # time-averaged retrograde flow rate, as a positive rate
        "F_mean": -trac_sum / n_steps,   # time-averaged traction force, as a positive magnitude
        "F_max": trac_min,               # largest traction force reached, signed as in the model
    }


def run(inputs, settings):
    i = inputs
    return simulate(i["nm"], i["Fm"], i["vu"], i["nc"], i["kon"], i["koff"], i["Fb"], i["kc"], i["ksub"], settings)
