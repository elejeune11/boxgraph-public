# Motor-clutch model with the lattice removed (Supplementary Note 1, "Supplemental Model
# Characterization"; Supplementary Fig. 1d): nc clutches, each connected to its own independent
# substrate spring of stiffness ksub. Units: nm, pN, s.
#
# Each time step, as in the flowchart of Supplementary Fig. 1b:
#   1. an unbound clutch binds with probability 1 - exp(-kon dt) (kon, Supp. Table 2);
#      a newly bound clutch starts unstretched;
#   2. every bound clutch-plus-substrate-spring pair is stretched by v_retrograde dt;
#      the clutch spring (kclutch) and the substrate spring (ksub) are in series;
#   3. each bound clutch unbinds with probability 1 - exp(-koff* dt),
#      koff* = koff exp(Fclutch / Frup) (Bell model, Supp. Note 1);
#   4. v_retrograde = vu (1 - sum Fclutch / Fstall) (Supp. Eq. 1), and
#      v_spread = vu - v_retrograde.
# The output is v_spread averaged over the run.
import numpy as np


def simulate(nc, kon, koff, Frup, vu, Fstall, kc, ksub, settings):
    dt = settings["dt"]
    n_steps = int(round(settings["t_total"] / dt))
    rng = np.random.default_rng(settings["seed"])
    n = int(round(nc))
    keff = kc * ksub / (kc + ksub)               # clutch and substrate spring in series
    p_on = 1.0 - np.exp(-kon * dt)
    bound = np.zeros(n, dtype=bool)
    ext = np.zeros(n)                            # extension of each clutch-substrate pair
    v_retro = vu                                 # no adhesions: retrograde flow at vu
    v_sum = 0.0
    with np.errstate(over="ignore"):
        for _ in range(n_steps):
            new = (~bound) & (rng.random(n) < p_on)
            ext[new] = 0.0
            bound |= new
            ext[bound] += v_retro * dt
            F = keff * ext
            koff_star = koff * np.exp(F / Frup)
            off = bound & (rng.random(n) < 1.0 - np.exp(-koff_star * dt))
            bound &= ~off
            ext[~bound] = 0.0
            F_sum = keff * ext[bound].sum()
            v_retro = vu * (1.0 - F_sum / Fstall)
            v_sum += vu - v_retro
    return {"v_spread": v_sum / n_steps}


def run(inputs, settings):
    i = inputs
    return simulate(i["nc"], i["kon"], i["koff"], i["Frup"], i["vu"], i["Fstall"], i["kclutch"], i["ksub"], settings)
