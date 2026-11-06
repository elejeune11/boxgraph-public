import math

import numpy as np
from scipy.integrate import quad

EV_ERG = 1.602176634e-12


def run(inputs, settings):
    # In n = Nb/N1 and s = k- t, Eq. 17 reads dn/ds = KN2 (1 - n) - n exp(Y/n),
    # with Y = r0 f/kT and f = F/N1 (gamma = r0). Above the critical force dn/ds < 0
    # on (0, n0], so the time to go from n0 to n_stop is s = int dn / (n e^(Y/n) - KN2 (1 - n)).
    K = inputs["KN2"]
    Y = inputs["r0"] * 1e-7 * inputs["f"] / EV_ERG / inputs["kT"]
    n0 = K / (1 + K)
    n_stop = settings["n_stop"]

    def loss(n):
        return n * math.exp(min(Y / n, 700.0)) - K * (1 - n)

    grid = np.linspace(n_stop, n0, settings["n_grid"])
    if min(loss(n) for n in grid) <= 0:
        return {"t": float("inf")}  # an equilibrium survives: the force is below critical
    s, _ = quad(lambda n: 1.0 / loss(n), n_stop, n0, epsrel=settings["rtol"], epsabs=0.0, limit=1000)
    return {"t": s / inputs["k_minus"]}
