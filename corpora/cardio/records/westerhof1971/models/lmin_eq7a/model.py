MMHG_DYN_CM2 = 1333.22387415  # 1 mm Hg in dyne/cm^2


def run(inputs, settings):
    r = inputs["d"] / 10.0 / 2.0  # cm
    c7a = 1.0 / (8.0 * inputs["Re"])
    k_cgs = c7a * r**3 * inputs["rho"] / inputs["mu"] ** 2  # cm per (dyne/cm^2)
    return {"c7a": c7a, "k11a": k_cgs * MMHG_DYN_CM2}


def symbolic():
    import sympy as sp
    Re, d, rho, mu = sp.symbols("Re d rho mu", positive=True)
    r = d / 20
    c7a = 1 / (8 * Re)
    return {"c7a": c7a, "k11a": c7a * r**3 * rho / mu**2 * MMHG_DYN_CM2}
