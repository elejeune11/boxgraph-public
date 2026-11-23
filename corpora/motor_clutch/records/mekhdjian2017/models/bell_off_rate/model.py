# The single-exponential Bell off-rate of one engaged clutch, the rule motor_clutch_reinforced applies
# to each clutch (kb = koff exp(Fclutch/Fb) there). Units: pN, 1/s.
import math


def run(inputs, settings):
    return {"koff_star": inputs["koff"] * math.exp(inputs["Fclutch"] / inputs["Fb"])}


def symbolic():
    import sympy as sp
    koff, Fclutch, Fb = sp.symbols("koff Fclutch Fb", positive=True)
    return {"koff_star": koff * sp.exp(Fclutch / Fb)}
