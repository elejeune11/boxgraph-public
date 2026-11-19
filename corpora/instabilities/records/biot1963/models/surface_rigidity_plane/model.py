import math


def run(inputs, settings):
    lam = inputs["lam"]
    zeta = (1 - lam**4) / (1 + lam**4)            # Eq. 4.2: P/(2 mu) in plane strain
    k = math.sqrt((1 - zeta) / (1 + zeta))         # Eq. 2.8
    if zeta == 0:
        phi = 1.0                                  # the paper: "for P = zeta = 0, we derive phi = 1"
    else:
        phi = (k * (1 + zeta) ** 2 - 1) / zeta     # Eq. 4.8
    mu = 0.5 * (lam**2 + 1 / lam**2)               # Eq. 3.25, mu/mu0
    return {"rigidity": mu * phi}                  # Eq. 4.10
