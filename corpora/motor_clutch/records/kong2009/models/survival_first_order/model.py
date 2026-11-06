# One population of bonds dissociating at a first-order rate k: the number still bound at t is N0 exp(-k t),
# so ln(number of events with lifetime >= t) falls on a line of slope -k (p. 8, Fig. S5).


def run(inputs, settings):
    return {"lnN": inputs["lnN0"] - inputs["k"] * inputs["t"]}


def symbolic():
    import sympy as sp

    lnN0, k, t = sp.symbols("lnN0 k t", positive=True)
    return {"lnN": lnN0 - k * t}
