import math

import numpy as np
from scipy.linalg import expm


def run(inputs, settings):
    # Exact mean of Eq. 1 by the matrix exponential; the paper's curves (Figs. 3a, 3d) are
    # Monte Carlo (Gillespie) estimates of the same mean.
    n0, g = int(round(inputs["N0"])), inputs["gamma"]
    f = inputs["f_over_N0"] * n0
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
    return {"N": float(np.arange(n0 + 1) @ p)}
