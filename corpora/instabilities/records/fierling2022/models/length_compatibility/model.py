# A section of length L holds a ventral segment L/n. If the segment shortens by e (relative) and L is
# unchanged ("if the embryo shape is unchanged"), the remaining length L (n - 1)/n gains e L/n:
# its stretch is e/(n - 1).


def run(inputs, settings):
    e = inputs["e"]
    s_ap = e / (inputs["n_ap"] - 1.0)
    s_dv = e / (inputs["n_dv"] - 1.0)
    return {"s_ap": s_ap, "s_dv": s_dv, "ratio": s_ap / s_dv}


def symbolic():
    import sympy as sp
    e, na, nd = sp.symbols("e n_ap n_dv", positive=True)
    return {"s_ap": e / (na - 1), "s_dv": e / (nd - 1), "ratio": (nd - 1) / (na - 1)}
