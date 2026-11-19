# The N-mode post-bifurcation equations (4.6) for a first-mode imperfection (xibar_n = 0 for n > 1),
# with the printed coefficients of Eq. 4.3 (b224 = 4 b112, b336 = 9 b112, b246 = 4 b123 as printed),
# N <= 6 (the coefficients printed). Scaling lambda - lambda_W = lambda_W sqrt(xibar_1) D and
# xi_n = lambda_W sqrt(xibar_1) eta_n removes lambda_W and xibar_1:
#     2 n D eta_n + dC/deta_n = 2 c delta_n1,   C = sum b_ijm eta_i eta_j eta_m,
# so lambda* - lambda_W = c* lambda_W sqrt(xibar_1) with c* = the minimum of D on the equilibrium path
# that starts at small amplitude (large D, eta_1 ~ c/D). The path is followed in eta_1 (Newton from the
# previous point); the minimum of D is then located by golden-section search between grid points.
import numpy as np
from scipy.optimize import fsolve, minimize_scalar


def coefficients(inputs):
    b112, b123 = inputs["b112"], inputs["b123"]
    return {(1, 1, 2): b112, (1, 2, 3): b123, (2, 2, 4): 4.0 * b112, (1, 3, 4): inputs["b134"],
            (2, 3, 5): inputs["b235"], (1, 4, 5): inputs["b145"], (1, 5, 6): inputs["b156"],
            (2, 4, 6): 4.0 * b123, (3, 3, 6): 9.0 * b112}


def grad(b, eta, N):
    g = np.zeros(N)
    for (i, j, m), v in sorted(b.items()):
        if m > N:
            continue
        idx = (i - 1, j - 1, m - 1)
        for p in range(3):
            o = [idx[q] for q in range(3) if q != p]
            g[idx[p]] += v * eta[o[0]] * eta[o[1]]
    return g


def residual(u, eta1, b, c, N):
    D = u[0]
    eta = np.concatenate([[eta1], u[1:]])
    n = np.arange(1, N + 1)
    res = 2.0 * n * D * eta + grad(b, eta, N)
    res[0] -= 2.0 * c
    return res


def solve_at(eta1, guess, b, c, N, xtol):
    u, _info, ier, _msg = fsolve(residual, guess, args=(eta1, b, c, N), full_output=True, xtol=xtol)
    return u, ier == 1


def path(inputs, settings):
    N = int(round(inputs["N"]))
    if N < 2 or N > 6:
        raise ValueError("Eq. 4.3 prints the coefficients for N <= 6 only")
    b = coefficients(inputs)
    c = inputs["c"]
    xtol = float(settings.get("xtol", 1e-12))
    etas = np.linspace(float(settings.get("eta_min", 0.01)), float(settings.get("eta_max", 3.0)),
                       int(settings.get("n_steps", 1500)))
    u = np.concatenate([[c / etas[0]], np.zeros(N - 1)])
    sols = []
    for e1 in etas:
        u, _ok = solve_at(e1, u, b, c, N, xtol)
        sols.append(u.copy())
    return N, b, c, xtol, etas, sols


def cstar_max_strain(inputs, settings):
    N, b, c, xtol, etas, sols = path(inputs, settings)
    D = np.array([s[0] for s in sols])
    i = int(np.argmin(D))
    i = min(max(i, 1), len(etas) - 2)
    guess = sols[i]

    def Dof(e1):
        return solve_at(e1, guess, b, c, N, xtol)[0][0]

    res = minimize_scalar(Dof, bounds=(etas[i - 1], etas[i + 1]), method="bounded",
                          options={"xatol": 1e-10})
    return float(min(res.fun, D[i]))


def run(inputs, settings):
    return {"cstar": cstar_max_strain(inputs, settings)}
