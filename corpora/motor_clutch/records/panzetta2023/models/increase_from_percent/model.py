# Increase of the optimal nc in clutches from the printed increase in percent and the printed
# control optimum: dn = n_ref * pct / 100. Used to check the "+1 clutch" of p. 9 against the
# "3 %" of p. 6 on the soft substrate.


def run(inputs, settings):
    return {"dn": inputs["n_ref"] * inputs["pct"] / 100.0}


def symbolic():
    import sympy as sp
    n_ref, pct = sp.symbols("n_ref pct", positive=True)
    return {"dn": n_ref * pct / 100}
