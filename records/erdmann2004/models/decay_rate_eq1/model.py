import math

import numpy as np


def run(inputs, settings):
    # Generator of Eq. 1 restricted to the transient states i = 1..N0 (i = 0 absorbing).
    # At long times N(tau) decays as exp(-a tau), with a the slowest decay eigenvalue.
    n0, g, f = int(round(inputs["N0"])), inputs["gamma"], inputs["f"]
    Q = np.zeros((n0, n0))
    for i in range(1, n0 + 1):
        r_i, g_i, k = i * math.exp(f / i), g * (n0 - i), i - 1
        Q[k, k] -= r_i + g_i
        if i > 1:
            Q[k - 1, k] += r_i
        if i < n0:
            Q[k + 1, k] += g_i
    return {"a": float(-max(np.linalg.eigvals(Q).real))}
