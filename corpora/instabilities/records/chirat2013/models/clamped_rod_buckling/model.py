# Linearized Eq. 4 about the flat state: with theta small, y' = theta, theta' = m, m' = nx theta - ny,
# ny' = kf y and nx = -P constant (x - px is second order), which gives y'''' + P y'' + kf y = 0 on [0, 1].
# Clamped ends: y = y' = 0 at 0 and 1. Finite differences on n_grid intervals with mirror ghost nodes
# (y_-1 = y_1) give (D4 + kf) y = P (-D2) y, a symmetric generalized eigenproblem; the lowest P buckles first.
# parity "any": the lowest mode of all; parity "symmetric": the lowest mode symmetric about s0 = 1/2
# (a single centred bulge, as a solver seeking one spine would find).
import numpy as np
from scipy.linalg import eigh


def _matrices(kf, n):
    h = 1.0 / n
    m = n - 1  # interior nodes
    d4 = np.zeros((m, m))
    for i in range(m):
        for off, c in ((-2, 1.0), (-1, -4.0), (0, 6.0), (1, -4.0), (2, 1.0)):
            j = i + off
            if 0 <= j < m:
                d4[i, j] += c
    d4[0, 0] += 1.0  # ghost y_-1 = y_1
    d4[m - 1, m - 1] += 1.0  # ghost y_n+1 = y_n-1
    d4 /= h ** 4
    d2 = (np.diag(-2.0 * np.ones(m)) + np.diag(np.ones(m - 1), 1) + np.diag(np.ones(m - 1), -1)) / h ** 2
    return d4 + kf * np.eye(m), -d2


def run(inputs, settings):
    kf = float(inputs["kf"])
    n = int(settings.get("n_grid", 400))
    parity = settings.get("parity", "any")
    a, b = _matrices(kf, n)
    vals, vecs = eigh(a, b, subset_by_index=[0, 11])
    pick = 0
    if parity == "symmetric":
        pick = next(j for j in range(len(vals)) if float(vecs[:, j] @ vecs[::-1, j]) > 0)
    v = vecs[:, pick]
    v = v[np.abs(v) > 1e-8 * np.max(np.abs(v))]
    changes = int(np.sum(np.sign(v[1:]) != np.sign(v[:-1])))
    return {"mode": float(changes + 1), "P": float(vals[pick])}
