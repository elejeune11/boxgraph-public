import math


def run(inputs, settings):
    b1, t = inputs["beta1"], inputs["t"]
    lq = 1 / b1**2
    lp = (1 - 32 / b1**4) / b1**2
    alpha = math.pi / 8
    return {"q": alpha * (1 - lp / lq) * math.exp(-t / lq)}


def symbolic():
    import sympy as sp
    b1, t = sp.symbols("beta1 t", positive=True)
    lq = 1 / b1**2
    lp = (1 - 32 / b1**4) / b1**2
    return {"q": sp.pi / 8 * (1 - lp / lq) * sp.exp(-t / lq)}
