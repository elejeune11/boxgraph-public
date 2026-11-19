# The Biot critical strain as the paper places it (p. 5): the strain at which kbar of Eq. 2.8 diverges,
# i.e. where its denominator first vanishes for 0 < lambda < 1. Of the three factors only
# lambda^3 + lambda^2 + lambda - 1 changes sign in that interval.
def run(inputs, settings):
    from scipy.optimize import brentq

    def den(lam):
        return (lam**6 - lam**4 + 3 * lam**2 + 1) * (lam**3 + lam**2 + lam - 1) * (lam**3 - lam**2 + lam + 1)

    lam_b = brentq(den, 0.1, 0.99, xtol=1e-14)
    return {"eps_B": 1.0 - lam_b}
