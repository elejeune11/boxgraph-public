# The same parent with two terminal daughters as reduced_resistance_s10, solved directly as a Poiseuille
# network from the equations Eq. S10 is said to combine (p. 4): Eq. S1 for each vessel's resistance,
# Eqs. S2-S4 for the daughters in parallel below the parent, and Eq. S7 to refer the result to the
# parent radius. Radii: any parent radius r_p (it cancels; 1 cm here), daughters r_k = beta_k r_p with
# beta from Eqs. S6 and S9 as in reduced_resistance_s10.
import math


def run(inputs, settings):
    mu = inputs["mu"] / 100.0
    g = inputs["gamma"]
    ra_star = 8 * mu * inputs["l_a"] / math.pi
    rb_star = 8 * mu * inputs["l_b"] / math.pi
    q = (rb_star * inputs["Q_b"] / (ra_star * inputs["Q_a"])) ** 0.25
    ba = (1 + q ** g) ** (-1 / g)
    bb = (1 + q ** (-g)) ** (-1 / g)
    rp = 1.0
    ra, rb = ba * rp, bb * rp

    def res(length, r):                       # Eq. S1
        return 8 * mu * length / (math.pi * r ** 4)

    R_a, R_b, R_p = res(inputs["l_a"], ra), res(inputs["l_b"], rb), res(inputs["l_p"], rp)
    R_total = R_p + 1.0 / (1.0 / R_a + 1.0 / R_b)   # Eqs. S2-S4: series parent, parallel daughters
    return {"Rstar_p": R_total * rp ** 4}           # Eq. S7
