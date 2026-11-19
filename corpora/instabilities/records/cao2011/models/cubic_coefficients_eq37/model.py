# Eq. 3.7 evaluated with the Biot modes (2.9)-(2.10), giving the b_ijm of Eq. 4.3 (built_from:
# quadratic_coefficient_eq38, for the modes and A).
# (1/6) d3Phi/dU^3 U^3 = (mu/lambda_1) Int I3 dV,  I3 = -(lambda_1 Q)(U1,1 U2,2 - U1,2 U2,1),
# with U = sum xi_n u^(n). The coefficient of xi_i xi_j xi_m is the sum over the distinct
# assignments of (i, j, m) to the three factors; divided by A it is b_ijm (Eq. 4.3).
import importlib.util
import itertools
import pathlib

import numpy as np
from scipy.integrate import quad

_path = pathlib.Path(__file__).resolve().parent.parent / "quadratic_coefficient_eq38" / "model.py"
_spec = importlib.util.spec_from_file_location("cao2011_quadratic_coefficient_eq38", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

TRIPLES = {"b112": (1, 1, 2), "b123": (1, 2, 3), "b134": (1, 3, 4), "b235": (2, 3, 5),
           "b145": (1, 4, 5), "b156": (1, 5, 6)}


def term(r, a, b, c, x1, depth):
    def integrand(x2):
        fa = _base.fields(r, a, x2, x1)
        fb = _base.fields(r, b, x2, x1)
        fc = _base.fields(r, c, x2, x1)
        return float(np.mean(-fa[4] * (fb[0] * fc[1] - fb[2] * fc[3])))

    return quad(integrand, -depth, 0.0, limit=400, epsabs=1e-13, epsrel=1e-12)[0]


def run(inputs, settings):
    r = inputs["r"]
    x1 = _base.grid(int(settings.get("n_x1", 64)))
    depth = float(settings.get("depth", 12.0))
    A = _base.coefficient_A(r, settings)
    out = {}
    for name, t in sorted(TRIPLES.items()):
        out[name] = sum(term(r, *p, x1, depth) for p in sorted(set(itertools.permutations(t)))) / A
    return out
