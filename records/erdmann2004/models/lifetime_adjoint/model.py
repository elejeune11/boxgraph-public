import math

import numpy as np


def run(inputs, settings):
    # Adjoint (backward) equation for the mean first passage time T_i to i = 0, in tau:
    # r(i) (T_{i-1} - T_i) + g(i) (T_{i+1} - T_i) = -1, with T_0 = 0 and g(N0) = 0.
    n0, g, f = int(round(inputs["N0"])), inputs["gamma"], inputs["f"]
    A = np.zeros((n0, n0))
    for i in range(1, n0 + 1):
        r_i, g_i, k = i * math.exp(f / i), g * (n0 - i), i - 1
        A[k, k] = -(r_i + g_i)
        if i > 1:
            A[k, k - 1] = r_i
        if i < n0:
            A[k, k + 1] = g_i
    T = np.linalg.solve(A, -np.ones(n0))
    return {"T": float(T[-1]) / inputs["k0"]}
