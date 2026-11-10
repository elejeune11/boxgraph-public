# Variant of reduced_resistance_s10: Eq. S10 with beta_k^4 in place of beta_k, the form that follows from
# Eqs. S1, S2, S4 and S7 for daughters in parallel and the form svv's code uses
# (svv/tree/utils/c_update.py lines 35-37). Everything else as in reduced_resistance_s10.
import math

POWER = 4.0


def _rstar(inputs, power):
    mu = inputs["mu"] / 100.0
    ra = 8 * mu * inputs["l_a"] / math.pi
    rb = 8 * mu * inputs["l_b"] / math.pi
    g = inputs["gamma"]
    q = (rb * inputs["Q_b"] / (ra * inputs["Q_a"])) ** 0.25
    ba = (1 + q ** g) ** (-1 / g)
    bb = (1 + q ** (-g)) ** (-1 / g)
    return 8 * mu * inputs["l_p"] / math.pi + 1.0 / (ba ** power / ra + bb ** power / rb)


def run(inputs, settings):
    return {"Rstar_p": _rstar(inputs, POWER)}
