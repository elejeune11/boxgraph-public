"""kim2010's lumped coronary vascular bed (p. 4: coefficients p0..p2, q0..q2, b0, b1), restated in our
own code to check the released block against the paper it cites.

The coefficients are those of the ordinary differential equation
    p0 P + p1 dP/dt + p2 d2P/dt2 = q0 Q + q1 dQ/dt + q2 d2Q/dt2 + b0 Pim + b1 dPim/dt
(the equation kim2010 replaces the outlet pressure with; its operators M, H solve it). Driven by a
sinusoidal inlet pressure and intramyocardial pressure, its periodic solution is exact in the
frequency domain:
    Q(t) = P_mean / q0 + Re[ (p(iw) P1 - b(iw) Pim1) / q(iw) e^(iwt) ]
with P1 = -i P_amp (P = P_mean + P_amp sin wt) and Pim1 = -Pim_amp (Pim = Pim_mean - Pim_amp cos wt).
The paper's equation has no venous pressure; b0 = 0, so the mean of Pim does not enter.
Units: P in mmHg, R in 10^3 dyn s/cm^5, C in 10^-6 cm^5/dyn (Table 3); Q is returned in cm^3/s.
"""
import math

MMHG = 1333.22387415


def _coef(Ra, Ram, Rv, Ca, Cim):
    p0 = 1.0
    p1 = Ram * Ca + Rv * (Ca + Cim)
    p2 = Ca * Cim * Ram * Rv
    q0 = Ra + Ram + Rv
    q1 = Ra * Ca * (Ram + Rv) + Cim * (Ra + Ram) * Rv
    q2 = Ca * Cim * Ra * Ram * Rv
    b0 = 0.0
    b1 = Cim * Rv
    return p0, p1, p2, q0, q1, q2, b0, b1


def run(inputs, settings):
    n = int(settings.get("n_pts", 501))
    Ra, Ram, Rv = (inputs[k] * 1e3 for k in ("Ra", "Ram", "Rv"))  # dyn s/cm^5
    Ca, Cim = inputs["Ca"] * 1e-6, inputs["Cim"] * 1e-6  # cm^5/dyn
    p0, p1, p2, q0, q1, q2, b0, b1 = _coef(Ra, Ram, Rv, Ca, Cim)
    T = inputs["T"]
    w = 2 * math.pi / T
    s = 1j * w
    P_mean = inputs["P_mean"] * MMHG
    P1 = -1j * inputs["P_amp"] * MMHG
    Pim1 = -inputs["Pim_amp"] * MMHG
    Q1 = ((p0 + p1 * s + p2 * s * s) * P1 - (b0 + b1 * s) * Pim1) / (q0 + q1 * s + q2 * s * s)
    Q0 = (p0 * P_mean - b0 * inputs["Pim_mean"] * MMHG) / q0
    ts = [T * k / (n - 1) for k in range(n)]
    q = [Q0 + (Q1 * complex(math.cos(w * t), math.sin(w * t))).real for t in ts]
    return {"Q_mean": Q0, "Q_max": max(q), "Q_min": min(q)}
