MMHG_DYN_CM2 = 1333.22387415  # 1 mm Hg in dyne/cm^2


def run(inputs, settings):
    r = inputs["d"] / 10.0 / 2.0  # cm
    # (a/8)(r/l) Re <= eps with Re = DeltaP r^3 rho / (8 mu^2 l)  ->  l^2 >= a r^4 rho DeltaP / (64 eps mu^2)
    k_cgs = inputs["a"] / (64.0 * inputs["eps"]) * r**4 * inputs["rho"] / inputs["mu"] ** 2  # cm^2 per dyne/cm^2
    return {"k11b": k_cgs * MMHG_DYN_CM2}


def symbolic():
    import sympy as sp
    a, eps, d, rho, mu = sp.symbols("a eps d rho mu", positive=True)
    r = d / 20
    return {"k11b": a / (64 * eps) * r**4 * rho / mu**2 * MMHG_DYN_CM2}
