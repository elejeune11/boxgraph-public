# Stochastic motor-clutch model with talin unfolding, refolding and vinculin binding
# (Supplementary Note, PDF pp. 23-25), made runnable from the words. Our code.
#
# Units of the ports: forces pN, lengths nm, times s, E kPa, traction Pa, speeds nm/s,
# densities 1/um^2, kont um^2/s, kc nN/nm (converted to pN/nm here).
#
# One time step (dt) of the note's cycle:
#  1. unbound fibronectin molecules bind, each with probability 1 - exp(-kon dt), kon = kont dint
#     (unbound clutches are interchangeable, so only their number is kept: the number binding in a step is
#     binomial; a newly bound clutch starts at the substrate position, unloaded);
#  2. for each clutch bound at the start of the step, with force f from the previous step: an unbinding
#     time ~ Exp(koff(f)) and, if its talin has not yet bound vinculin, an unfolding time ~ Exp(kunf(FR f));
#     if unfolding comes first and within dt, vinculin binding ~ Exp(kvin) races refolding ~ Exp(kfold(FR f)):
#     vinculin first -> reinforcement, dint += dadd, and that clutch's talin stays vinculin-bound; refolding
#     first -> nothing. Otherwise, if unbinding falls within dt the clutch unbinds, and dint -= dadd unless
#     its talin had bound vinculin; dint never drops below its basal value;
#  3. the actin filament moves at v = vu (1 - Fsub/(nm Fm)) (not below 0), dragging the bound clutches by
#     v dt; force balance gives the substrate position xsub = kc sum(x_i) / (ksub + nb kc), the clutch forces
#     kc (x_i - xsub) and the substrate force Fsub = ksub xsub.
# Outputs are time averages over the run of Fsub / (pi ra^2), of v and of dint. ksub = c E ra.
import math

import numpy as np

UNFOLDING = True   # the model "with talin unfolding"; clutch_no_talin_sim calls simulate(unfolding=False)


def koff_of(f, p):
    """Catch bond: sum of two exponentials, plus the added low-force term, times the scaling factor."""
    f = np.abs(f)
    h = -math.log(0.1 / p["koff_g"]) / p["koff_fend"] if p["koff_g"] > 0 else 0.0
    k = p["koff_a"] * np.exp(p["koff_b"] * f) + p["koff_c"] * np.exp(p["koff_d"] * f)
    if p["koff_g"] > 0:
        k = k + p["koff_g"] * np.exp(-h * f)
    return p["koff_scale"] * k


def simulate(p, s, unfolding=UNFOLDING):
    rng = np.random.default_rng(int(s.get("seed", 1)))
    dt = float(s["dt"])
    n_steps = int(round(float(s["t_total"]) / dt))
    nf = int(round(p["nf"]))
    kc = p["kc"] * 1000.0                                  # nN/nm -> pN/nm
    ksub = p["ksub_factor"] * p["E"] * 1e-3 * p["ra"]      # kPa = 1e-3 pN/nm^2
    Fstall = p["nm"] * p["Fm"]
    vu = p["vu"]
    d0 = p["dint"]
    dint = d0
    x = np.zeros(0)                 # positions of the bound clutches
    vinc = np.zeros(0, dtype=bool)  # their talin has bound vinculin
    xsub = 0.0
    Fsub = 0.0
    sumF = sumV = sumD = 0.0
    for _ in range(n_steps):
        nb = x.size
        # 1. binding of unbound fibronectin molecules
        pb = 1.0 - math.exp(-p["kont"] * dint * dt)
        n_new = rng.binomial(nf - nb, pb) if nf > nb else 0
        # 2. unbinding / unfolding of the clutches bound at the start of the step
        if nb:
            f = kc * (x - xsub)
            t_ub = rng.exponential(1.0, nb) / koff_of(f, p)
            if unfolding:
                ft = p["FR"] * np.abs(f)
                t_uf = rng.exponential(1.0, nb) / np.exp(p["ln_kunf0"] + p["kunf_b"] * ft)
                unf = ~vinc & (t_uf < t_ub) & (t_uf < dt)
                t_v = rng.exponential(1.0, nb) / p["kvin"]
                t_f = rng.exponential(1.0, nb) / np.exp(p["ln_kfold0"] + p["kfold_b"] * ft)
                newv = unf & (t_v < t_f)
                unb = ~unf & (t_ub < dt)
                n_loss = int((unb & ~vinc).sum())
                vinc = vinc | newv
                dint = max(d0, dint + p["dadd"] * (int(newv.sum()) - n_loss))
            else:
                unb = t_ub < dt
            keep = ~unb
            x = x[keep]
            vinc = vinc[keep]
        if n_new:
            x = np.concatenate([x, np.full(n_new, xsub)])
            vinc = np.concatenate([vinc, np.zeros(n_new, dtype=bool)])
        # 3. actin moves; force balance
        v = vu * max(0.0, 1.0 - Fsub / Fstall)
        nb = x.size
        if nb:
            x = x + v * dt
            xsub = kc * x.sum() / (ksub + nb * kc)
        else:
            xsub = 0.0
        Fsub = ksub * xsub
        sumF += Fsub
        sumV += v
        sumD += dint
    traction = (sumF / n_steps) / (math.pi * p["ra"] ** 2) * 1e6   # pN/nm^2 -> Pa
    return {"traction": traction, "actin_flow": sumV / n_steps, "dint_mean": sumD / n_steps}


def run(inputs, settings):
    return simulate(dict(inputs), settings)
