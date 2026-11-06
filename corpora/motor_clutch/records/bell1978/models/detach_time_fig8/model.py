import math

import numpy as np
from scipy.integrate import quad


def run(inputs, settings):
    # As detach_time_eq17, in Fig. 8's variables: r0 f/kT = f* ln(KN2) and s = k- t = t*.
    # dn/ds = KN2 (1 - n) - n exp(Y/n), so t* = int dn / (n e^(Y/n) - KN2 (1 - n)) from n_stop to n0.
    K = inputs["KN2"]
    Y = inputs["f_star"] * math.log(K)
    n0 = K / (1 + K)
    n_stop = settings["n_stop"]

    def loss(n):
        return n * math.exp(min(Y / n, 700.0)) - K * (1 - n)

    grid = np.linspace(n_stop, n0, settings["n_grid"])
    if min(loss(n) for n in grid) <= 0:
        return {"log10_t_star": float("inf")}  # an equilibrium survives: the force is below critical
    s, _ = quad(lambda n: 1.0 / loss(n), n_stop, n0, epsrel=settings["rtol"], epsabs=0.0, limit=1000)
    return {"log10_t_star": math.log10(s)}
