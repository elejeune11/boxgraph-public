import math


def plog(a):
    # principal branch of x e^x = a for a >= 0, by Newton's method
    x = math.log1p(a)
    for _ in range(100):
        ex = math.exp(x)
        step = (x * ex - a) / (ex * (x + 1))
        x -= step
        if abs(step) < 1e-15 * max(1.0, abs(x)):
            break
    return x


def run(inputs, settings):
    return {"fc_over_N0": plog(inputs["gamma"] / math.e)}


def symbolic():
    import sympy as sp
    gamma = sp.symbols("gamma", positive=True)
    return {"fc_over_N0": sp.LambertW(gamma / sp.E)}
