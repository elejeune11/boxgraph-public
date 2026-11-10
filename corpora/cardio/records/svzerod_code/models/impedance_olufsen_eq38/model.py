"""olufsen2000's structured-tree outflow condition, Eq. 38, restated in our own code from the paper, to
check the released impedance block against the paper it cites:

  p(x_L, t) = integral over one period T of q(x_L, t - tau) z(x_L, tau) d tau          (Eq. 38)

discretized as the paper's Appendix B says (Fig. B3: the sum runs over a whole period, using this
period's values of q for the most recent steps and the previous period's for the rest): with
dt = T / N and periodic q,
  p_n = sum_{k=0}^{N-1} q_{n-k} z(t_k) dt.
Driven by q(t) = Q0 + Q1 sin(2 pi t / T) with the impulse response z(t) = (Z / tau) exp(-t / tau),
0 <= t < T. Outputs: mean, largest and smallest p_n over one period at the N + 1 points t_0..t_N.
"""
import math


def run(inputs, settings):
    N = int(settings.get("N", 128))
    T = inputs["T"]
    dt = T / N
    q = [inputs["Q0"] + inputs["Q1"] * math.sin(2 * math.pi * j * dt / T) for j in range(N)]
    z = [inputs["Z"] / inputs["tau"] * math.exp(-k * dt / inputs["tau"]) for k in range(N)]
    p = [sum(q[(n - k) % N] * z[k] * dt for k in range(N)) for n in range(N)]
    p_all = p + [p[0]]
    return {"P_mean": sum(p) / N, "P_max": max(p_all), "P_min": min(p_all)}
