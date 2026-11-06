import math


def run(inputs, settings):
    b1, p0, t = inputs["beta1"], inputs["p0"], inputs["t"]
    lq = 1 / b1**2
    lp = (1 - 32 / b1**4) / b1**2
    alpha = math.pi / 8
    return {"q": alpha * p0 * (1 - lp / lq) * math.exp(-t / lq)}


def symbolic():
    import sympy as sp
    b1, p0, t = sp.symbols("beta1 p0 t", positive=True)
    lq = 1 / b1**2
    lp = (1 - 32 / b1**4) / b1**2
    return {"q": sp.pi / 8 * p0 * (1 - lp / lq) * sp.exp(-t / lq)}
