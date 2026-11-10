# Eq. S6 (p. 4) for a bifurcation, C = {i, j}: beta_i = r_i/r_p = (1 + (r_j/r_i)^gamma)^(-1/gamma), and the
# same for j with the ratio inverted; output the sum the paper says is identically one (p. 4).
def run(inputs, settings):
    g, q = inputs["gamma"], inputs["ratio"]
    bi = (1.0 + q ** g) ** (-1.0 / g)
    bj = (1.0 + q ** (-g)) ** (-1.0 / g)
    return {"beta_i": bi, "beta_j": bj, "beta_sum": bi ** g + bj ** g}


def symbolic():
    import sympy as sp

    g, q = sp.symbols("gamma ratio", positive=True)
    bi = (1 + q ** g) ** (-1 / g)
    bj = (1 + q ** (-g)) ** (-1 / g)
    return {"beta_i": bi, "beta_j": bj, "beta_sum": bi ** g + bj ** g}
