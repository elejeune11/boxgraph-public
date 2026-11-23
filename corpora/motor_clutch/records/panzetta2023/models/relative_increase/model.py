# Increase of the optimal nc with respect to the control (no residual strain): in percent and in
# clutches, as the paper reports it (pp. 6, 7, 9).


def run(inputs, settings):
    n0, n = inputs["n_ref"], inputs["n"]
    return {"pct": 100.0 * (n / n0 - 1.0), "dn": n - n0}


def symbolic():
    import sympy as sp
    n_ref, n = sp.symbols("n_ref n", positive=True)
    return {"pct": 100 * (n / n_ref - 1), "dn": n - n_ref}
