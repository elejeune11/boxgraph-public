# Eq. S25 times R^3/K: P R^3/K = Lam (1 + 1/Lam) Delta with Lam = lambda R^2/K, and Delta the
# excess strain, given in Fig. S6B as a multiple x of the threshold of Eq. S21 (printed factor).
# Printed with "proportional to": prefactor 1.


def _dc(Lam):
    return (30.0 * 2.5 ** (2.0 / 3.0) / Lam) ** 0.6


def run(inputs, settings):
    Lam, x = inputs["Lam"], inputs["x"]
    return {"p": Lam * (1.0 + 1.0 / Lam) * x * _dc(Lam)}
