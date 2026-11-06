import math

import numpy as np
from scipy.linalg import expm


def run(inputs, settings):
    # Exact solution of the linear system Eq. 1 on states i = 0..N0 by the matrix exponential;
    # the paper estimates the same p_i(tau) by Monte Carlo (Gillespie) simulation.
    n0, g, f = int(round(inputs["N0"])), inputs["gamma"], inputs["f"]
    Q = np.zeros((n0 + 1, n0 + 1))
    for i in range(1, n0 + 1):
        r_i, g_i = i * math.exp(f / i), g * (n0 - i)
        Q[i, i] -= r_i + g_i
        Q[i - 1, i] += r_i
        if i < n0:
            Q[i + 1, i] += g_i
    p0 = np.zeros(n0 + 1)
    p0[n0] = 1.0
    p = expm(Q * inputs["tau"]) @ p0
    return {"p": float(p[int(round(inputs["i"]))])}
