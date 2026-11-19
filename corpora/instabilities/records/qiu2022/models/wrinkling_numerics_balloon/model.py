# Onset of wrinkling on the numerical energy minimum (energy_numerics_balloon), by the criterion the
# paper states in words on p. 3: wrinkling starts when the axial membrane force at the point of maximal
# compression reaches N_z^0 + Delta N_z = -sigma_c t, with sigma_c t = (2/rho) sqrt(D_z S_theta) (Eq. 10)
# and rho the circumferential radius of curvature there. Divided by S_z (with S_z alpha = sqrt(D_z S_theta)/R,
# which follows from alpha = sqrt(E_theta/12E_z) t/R and D = S t^2/12) and with N_z^0 = pR/2:
#   g(kappa) = p/2 + min_mu (e0 + kappa y) + 2 alpha (1 + phi'(mu*)) = 0,  mu* the most compressed point.
# The smallest kappa with g = 0 is found by stepping and bisection.
import importlib.util
import pathlib

import numpy as np
from scipy.optimize import brentq

_path = pathlib.Path(__file__).resolve().parent.parent / "energy_numerics_balloon" / "model.py"
_spec = importlib.util.spec_from_file_location("qiu2022_energy_numerics_balloon", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def margin(k, p, alpha, n_modes, n_grid):
    pr = _base.Problem(k, p, alpha, n_modes, n_grid)
    _, sol = pr.solve()
    i = int(np.argmin(sol["strain"]))
    return p / 2 + sol["strain"][i] + 2 * alpha * (1 + sol["dphi"][i])


def onset(p, alpha, settings):
    n_modes, n_grid = _base.settings_of(settings)
    n_steps = int(settings.get("n_steps", 60))
    k_max = 2.0 * np.sqrt(8 / 3 * alpha**2 + 8 / 9 * p)  # twice the Eq. 9 Brazier curvature
    ks = np.linspace(0, k_max, n_steps + 1)[1:]
    prev_k, prev_g = 0.0, p / 2 + 2 * alpha
    for k in ks:
        g = margin(k, p, alpha, n_modes, n_grid)
        if g <= 0:
            return brentq(margin, prev_k, k, args=(p, alpha, n_modes, n_grid), xtol=1e-9 * k_max, rtol=1e-10)
        prev_k, prev_g = k, g
    return float("nan")


def run(inputs, settings):
    return {"khat_w": float(onset(inputs["phat"], inputs["alpha"], settings))}
