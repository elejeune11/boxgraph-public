# Eq. 9: a~ = a3 * dbar + b3, with dbar the mean of proximal and distal lumen diameters (q_mean_diameter).


def run(inputs, settings):
    d = 0.5 * (inputs["d_prox"] + inputs["d_dist"])
    return {"va": inputs["a3"] * d + inputs["b3"]}


def symbolic():
    import sympy as sp
    d_prox, d_dist, b3 = sp.symbols("d_prox d_dist b3", positive=True)
    a3 = sp.Symbol("a3")
    return {"va": a3 * (d_prox + d_dist) / 2 + b3}
