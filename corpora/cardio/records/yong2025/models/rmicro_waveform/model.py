# Time-varying microvascular resistance at time t of the cycle, Eqs. 10-11 with e_n = e_v of Eq. 4:
# R(t) = [(kPH sqrt(k Rbar) - sqrt(f Rbar)) e_v(t) + sqrt(f Rbar)]^2 (kPH multiplies the root, as printed).
# Port units: mmHg*s/ml, percent, s.
import math


def run(inputs, settings):
    T = inputs["T"]
    t = inputs["t"] % T
    Tvc, Tvr = inputs["Tvc"], inputs["Tvr"]
    if t <= Tvc:
        e = 0.5 * (1.0 - math.cos(math.pi * t / Tvc))
    elif t <= Tvc + Tvr:
        e = 0.5 * (1.0 + math.cos(math.pi * (t - Tvc) / Tvr))
    else:
        e = 0.0
    Rbar = inputs["Rbar"]
    a = inputs["k_ph"] * math.sqrt(inputs["k"] * Rbar)
    b = math.sqrt(inputs["frac"] / 100.0 * Rbar)
    return {"R": ((a - b) * e + b) ** 2}
