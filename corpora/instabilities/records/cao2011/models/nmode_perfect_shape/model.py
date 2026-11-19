# The surface shape of the perfect N-mode solution (Fig. 3): xi_n = alpha_n (lambda - lambda_W)
# solves Eq. 4.6 with xibar = 0, i.e. 2 n alpha_n + dC/dalpha_n = 0 with C = sum b_ijm alpha_i
# alpha_j alpha_m (coefficients as in nmode_cstar_eq46, N <= 6 printed). As the paper describes
# (p. 105), the N - 1 solution, with alpha_N = 0, starts the iteration for N, from the two-mode
# solution alpha_1 = 2/b112, alpha_2 = -1/b112 of Eq. 4.8. The surface displacement is
# u2(x1, 0) = l sum xi_n cos(2 pi n x1/l) (the two-mode form printed on p. 104), so
#     u2(x1, 0)/[(lambda - lambda_W) l] = sum alpha_n cos(2 pi n x1/l).
import importlib.util
import math
import pathlib

import numpy as np
from scipy.optimize import fsolve

_path = pathlib.Path(__file__).resolve().parent.parent / "nmode_cstar_eq46" / "model.py"
_spec = importlib.util.spec_from_file_location("cao2011_nmode_cstar_eq46_shape", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def alphas(inputs, settings):
    N = int(round(inputs["N"]))
    if N < 2 or N > 6:
        raise ValueError("Eq. 4.3 prints the coefficients for N <= 6 only")
    b = _base.coefficients(inputs)
    xtol = float(settings.get("xtol", 1e-13))

    def res(a, n):
        k = np.arange(1, n + 1)
        return 2.0 * k * a + _base.grad(b, a, n)

    a = np.array([2.0 / inputs["b112"], -1.0 / inputs["b112"]])
    for n in range(3, N + 1):
        a = fsolve(res, np.concatenate([a, [0.0]]), args=(n,), xtol=xtol)
    return a


def run(inputs, settings):
    a = alphas(inputs, settings)
    x = inputs["x"]
    return {"u": float(sum(a[k] * math.cos(2.0 * math.pi * (k + 1) * x) for k in range(len(a))))}
