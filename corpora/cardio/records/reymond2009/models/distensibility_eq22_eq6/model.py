# Eq. 22 gives PWV from the mean lumen diameter d (mm) -> m/s; Eq. 6 gives C_A = A/(rho PWV^2),
# so the distensibility C_A/A = 1/(rho PWV^2), in 1/Pa. The mean diameter of a tapered segment is
# taken as the mean of its proximal and distal diameters (q_mean_diameter).


def run(inputs, settings):
    d = 0.5 * (inputs["d_prox"] + inputs["d_dist"])
    pwv = inputs["a2"] / d ** inputs["b2"]
    return {"D": 1.0 / (inputs["rho"] * pwv ** 2)}


def symbolic():
    import sympy as sp
    d_prox, d_dist, a2, b2, rho = sp.symbols("d_prox d_dist a2 b2 rho", positive=True)
    d = (d_prox + d_dist) / 2
    return {"D": 1 / (rho * (a2 / d ** b2) ** 2)}
