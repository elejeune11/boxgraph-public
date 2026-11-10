# Eq. S10 as printed (p. 4) for one parent vessel with two terminal daughters a and b:
#   terminal daughters: R*_k = 8 mu l_k / pi (Eq. S7 with Eq. S1; p. 4 "exactly (Eq. S7)")
#   daughter radius ratio, equal pressure drops (Eq. S9): r_b / r_a = (R*_b Q_b / (R*_a Q_a))^(1/4)
#   beta_a = (1 + (r_b/r_a)^gamma)^(-1/gamma), beta_b = (1 + (r_a/r_b)^gamma)^(-1/gamma)   (Eq. S6)
#   R*_p = 8 mu l_p / pi + (beta_a / R*_a + beta_b / R*_b)^-1                         (Eq. S10, printed)
# mu in cP (converted to poise), lengths in cm, flows in mL/s; R* in dyn s / cm.
import math

POWER = 1.0   # the power of beta_k in Eq. S10 as printed


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
