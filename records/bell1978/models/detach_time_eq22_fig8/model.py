import math

from scipy.special import exp1


def run(inputs, settings):
    Y0 = inputs["f_star"] * math.log(inputs["KN2"])  # r0 f/kT = f* ln(KN2)
    return {"log10_t_star": math.log10(float(exp1(Y0)))}


def symbolic():
    import sympy as sp
    f_star, KN2 = sp.symbols("f_star KN2", positive=True)
    return {"log10_t_star": sp.log(sp.expint(1, f_star * sp.log(KN2)), 10)}
