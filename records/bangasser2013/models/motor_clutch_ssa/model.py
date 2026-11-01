# Motor-clutch model simulated by the Gillespie SSA (Eq. 1; Supporting Material, "Model
# Simulation Algorithm", steps 1-8), with the Bell slip-bond off-rate and the force balance and
# force-velocity relation of Chan and Odde (2008), which the paper says it extends.
# Units: nm, pN, s. Positions and forces are taken positive in the retrograde direction.
import numpy as np


def off_rate(F, inputs):
    """Slip bond (Bell): koff* = koff exp(F/Fb)."""
    return inputs["koff"] * np.exp(F / inputs["Fb"])


def simulate(inputs, settings, off_rate=off_rate):
    nm, Fm, vu = inputs["nm"], inputs["Fm"], inputs["vu"]
    kon, kc, ksub = inputs["kon"], inputs["kc"], inputs["ksub"]
    n = int(round(inputs["nc"]))
    t_total = float(settings["t_total"])
    rng = np.random.default_rng(int(settings["seed"]))
    Fstall = nm * Fm
    bound = np.zeros(n, dtype=bool)
    x = np.zeros(n)          # clutch positions (the F-actin end), nm
    xsub = 0.0               # substrate position, nm
    t = 0.0
    v_int = 0.0              # time integrals for the averages
    F_int = 0.0
    n_int = 0.0
    n_fail = 0               # transitions to no engaged clutch
    v = vu
    with np.errstate(over="ignore"):
        while t < t_total:
            # 1. off-rate of each engaged clutch from its deformation
            F = kc * (x - xsub)
            rates = np.where(bound, off_rate(F, inputs), kon)
            # 2. event times by Eq. 1, t_event = -ln(URN)/k
            tev = -np.log(rng.random(n)) / rates
            # 3. advance time by the shortest event time
            i = int(np.argmin(tev))
            dt = float(tev[i])
            if not np.isfinite(dt):
                dt = t_total - t
            last = dt >= t_total - t
            dt = min(dt, t_total - t)
            n_eng = int(bound.sum())
            # 4. execute the reaction: bind (starting unstretched, at xsub) or unbind
            if not last:
                if bound[i]:
                    bound[i] = False
                else:
                    bound[i] = True
                    x[i] = xsub
            # 5. F-actin retrograde flow from the substrate deformation (linear force-velocity)
            v = vu * (1.0 - ksub * xsub / Fstall)
            # time averages over this step: the flow that moves the clutches, the traction
            # that sets it, and the clutches engaged during the interval
            v_int += v * dt
            F_int += ksub * xsub * dt
            n_int += n_eng * dt
            t += dt
            if last:
                break
            # 6. advance engaged clutches by flow x time step
            x[bound] += v * dt
            # 7. substrate position from the force balance on substrate and clutch springs
            n_new = int(bound.sum())
            xsub = kc * x[bound].sum() / (ksub + n_new * kc) if n_new else 0.0
            if n_eng > 0 and n_new == 0:
                n_fail += 1
    T = t if t > 0 else 1.0
    n_mean = n_int / T
    return {
        "v_retro": v_int / T,
        "F_mean": F_int / T,
        "n_eng": n_mean,
        "k_ens": kc * n_mean,
        "t_cycle": T / n_fail if n_fail else T,
    }


def run(inputs, settings):
    return simulate(inputs, settings)
