import math

N_A = 6.02214076e23
CAL_ERG = 4.184e7


def run(inputs, settings):
    # 2 pi r h sigma / (h/2) = 4 pi sigma r; cal/mol per angstrom -> erg per molecule per cm -> dyne
    per_r = 4 * math.pi * inputs["sigma"] * CAL_ERG / N_A / 1e-8  # dyne per angstrom of radius
    return {"f_per_r": per_r, "f": per_r * inputs["r"]}


def symbolic():
    import sympy as sp
    sigma, r = sp.symbols("sigma r", positive=True)
    per_r = 4 * sp.pi * sigma * CAL_ERG / N_A / 1e-8
    return {"f_per_r": per_r, "f": per_r * r}
