# Eqs. 30-31 driven by Pcs = Pm + (A/2) sin(w t), at periodic steady state. Eq. 30 is linear, so
# P~ = Pm + (A/2)|H(jw)| sin(w t + phi) with H = (1 + j w tau_z)/(1 + j w tau_p); the mean of the
# sigmoid (Eq. 31) over one period is the average over n_phase equally spaced phases (midpoint rule,
# exact to rounding for a smooth periodic integrand). Ports: mmHg, s, Hz, 1/s, percent.
import math


def run(inputs, settings):
    p = inputs
    pm = p["P_pct"] / 100.0 * p["P_ref"]
    w = 2.0 * math.pi * p["f_puls"]
    gain = abs(complex(1.0, w * p["tau_z"]) / complex(1.0, w * p["tau_p"]))
    amp = 0.5 * p["A_pp"] * gain
    n = int(settings["n_phase"])
    tot = 0.0
    for k in range(n):
        pt = pm + amp * math.sin(2.0 * math.pi * (k + 0.5) / n)
        e = math.exp((pt - p["Pn"]) / p["ka"])
        tot += (p["fmin"] + p["fmax"] * e) / (1.0 + e)
    return {"fcs_mean": tot / n}
