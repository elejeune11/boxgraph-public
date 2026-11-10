# Time-varying microvascular resistance, Eqs. 10-11:
# R(t) = [(kPH sqrt(k Rbar) - sqrt(f Rbar)) e_v(t) + sqrt(f Rbar)]^2, e_v from Eq. 4
# (Eq. 11 as printed: kPH multiplies the square root).
# Minimum (e = 0), maximum (e = 1) and the cycle average, in closed form: over one cycle
# mean(e) = (Tvc + Tvr)/(2T) and mean(e^2) = 3(Tvc + Tvr)/(8T) for the raised-cosine Eq. 4.
# Port units: mmHg*s/ml, percent, s.
import math


def run(inputs, settings):
    Rbar, f = inputs["Rbar"], inputs["frac"] / 100.0
    a = inputs["k_ph"] * math.sqrt(inputs["k"] * Rbar)
    b = math.sqrt(f * Rbar)
    D = (inputs["Tvc"] + inputs["Tvr"]) / inputs["T"]
    m1, m2 = D / 2.0, 3.0 * D / 8.0
    return {"R_min": b * b, "R_max": a * a,
            "R_mean": b * b + 2.0 * b * (a - b) * m1 + (a - b) ** 2 * m2}


def symbolic():
    import sympy as sp
    Rbar, frac, k, k_ph, Tvc, Tvr, T = sp.symbols("Rbar frac k k_ph Tvc Tvr T", positive=True)
    a = k_ph * sp.sqrt(k * Rbar)
    b = sp.sqrt(frac / 100 * Rbar)
    D = (Tvc + Tvr) / T
    return {"R_min": b ** 2, "R_max": a ** 2,
            "R_mean": b ** 2 + 2 * b * (a - b) * D / 2 + (a - b) ** 2 * 3 * D / 8}
