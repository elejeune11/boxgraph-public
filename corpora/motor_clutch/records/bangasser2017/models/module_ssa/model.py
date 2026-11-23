# One motor-clutch module of the CMS (reader's stand-in, see model.yaml `reconstructed`).
# Direct Gillespie method (Eqs. 10-11): one exponential waiting time from the total rate, one
# uniform number to pick the event. Off-rate by Eq. 1, motor retraction by Eq. 2, both loaded from
# their own model files. Order per event, after the paper's steps 2-8 and 11: rates, time to the
# next event, F-actin flow, advance engaged clutches by flow x time, execute the event, force
# balance (Eq. 4: κc Σ xc,i = κs xs). A newly bound clutch starts unstretched (at xs).
# Units: nm, pN, s. Retrograde direction positive.
import importlib.util
import math
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(f"bangasser2017_{name}", os.path.join(_HERE, "..", name, "model.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_eq1 = _load("off_rate_eq1")
_eq2 = _load("motor_velocity_eq2")


def simulate(inputs, settings):
    nm, Fm, vm = inputs["nm"], inputs["Fm"], inputs["vm"]
    kon, koff, Fb, kc, ks = inputs["kon"], inputs["koff"], inputs["Fb"], inputs["kc"], inputs["ks"]
    n = int(round(inputs["nc"]))
    t_total = float(settings["t_total"])
    rng = np.random.default_rng(int(settings["seed"]))
    bound = np.zeros(n, dtype=bool)
    x = np.zeros(n)
    xs = 0.0
    t = 0.0
    v_int = 0.0
    F_int = 0.0
    # Eq. 1 checked once against its model file; vectorised below in the same form
    assert abs(_eq1.run({"koff": koff, "Fc": Fb, "Fb": Fb}, {})["koff_i"] - koff * math.e) < 1e-9 * koff
    with np.errstate(over="ignore"):
        while t < t_total:
            Fc = kc * (x - xs)
            rates = np.where(bound, koff * np.exp(Fc / Fb), kon)          # Eq. 1 / kon
            R = float(rates.sum())
            u1, u2 = rng.random(), rng.random()
            dt = -math.log(u1) / R if R > 0 and np.isfinite(R) else (0.0 if R > 0 else t_total - t)  # Eq. 10
            last = dt >= t_total - t
            dt = min(dt, t_total - t)
            v = _eq2.run({"vm": vm, "ks": ks, "xs": xs, "nm": nm, "Fm": Fm}, {})["vm_j"]   # Eq. 2
            v_int += v * dt
            F_int += ks * xs * dt
            t += dt
            if last:
                break
            x[bound] += v * dt
            if np.isfinite(R):
                i = int(np.searchsorted(np.cumsum(rates), u2 * R, side="right"))    # Eq. 11
                i = min(i, n - 1)
            else:
                i = int(np.argmax(rates))
            if bound[i]:
                bound[i] = False
            else:
                bound[i] = True
                x[i] = xs
            nb = int(bound.sum())
            xs = kc * float(x[bound].sum()) / (ks + nb * kc) if nb else 0.0     # Eq. 4
    T = t if t > 0 else 1.0
    return {"v_flow": v_int / T, "F_trac": F_int / T}


def run(inputs, settings):
    return simulate(inputs, settings)
