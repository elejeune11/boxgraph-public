# Criterion (ii) of Table 1: the overall stretch at which the local stretch parallel to the surface at
# the deepest point, x1 = l/2, reaches lambda_W, on the N-mode path of Eq. 4.6 (built_from:
# nmode_cstar_eq46). The paper does not give this calculation ("a minor extension of the analysis in
# section 3"); this is the reader's reconstruction at the same asymptotic order:
#     lambda_A = lambda + U1,1(l/2, 0) = lambda + sum xi_n 2 pi n f(0) cos(n pi),  f(0) = (r - 1)/(r + 1)
# (U2,1 = 0 at x1 = l/2), and lambda_A = lambda_W, in the scaled variables of nmode_cstar_eq46:
#     D + 2 pi f(0) sum (-1)^n n eta_n = 0,
# taken at its first crossing along the path from small amplitude.
import importlib.util
import math
import pathlib

import numpy as np
from scipy.optimize import brentq

_path = pathlib.Path(__file__).resolve().parent.parent / "nmode_cstar_eq46" / "model.py"
_spec = importlib.util.spec_from_file_location("cao2011_nmode_cstar_eq46", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    N, b, c, xtol, etas, sols = _base.path(inputs, settings)
    r = inputs["r"]
    f0 = (r - 1.0) / (r + 1.0)
    n = np.arange(1, N + 1)
    sign = (-1.0) ** n

    def g(e1, u):
        eta = np.concatenate([[e1], u[1:]])
        return u[0] + 2.0 * math.pi * f0 * float(np.sum(sign * n * eta))

    vals = [g(e1, u) for e1, u in zip(etas, sols)]
    for i in range(1, len(etas)):
        if vals[i - 1] > 0.0 >= vals[i]:
            guess = sols[i]

            def h(e1):
                u = _base.solve_at(e1, guess, b, c, N, xtol)[0]
                return g(e1, u)

            e1 = brentq(h, etas[i - 1], etas[i], xtol=1e-12)
            return {"cstar": float(_base.solve_at(e1, guess, b, c, N, xtol)[0][0])}
    raise ValueError("lambda_A does not reach lambda_W on the computed path")
