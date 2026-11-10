# Ventricular elastance at time t of the cycle, Eqs. 3-4:
# E(t) = (Emax - Emin) e_v(t) + Emin, e_v = (1 - cos(pi t/Tvc))/2 for t <= Tvc,
# (1 + cos(pi (t - Tvc)/Tvr))/2 for Tvc < t <= Tvc + Tvr, 0 after. Port units: mmHg/ml, s.
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
    return {"E": (inputs["Emax"] - inputs["Emin"]) * e + inputs["Emin"]}
