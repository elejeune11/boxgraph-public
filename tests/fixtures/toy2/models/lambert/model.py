import math


def run(i, s):
    # solve w * exp(w) = k0 (in units of 1/s) by Newton's method: tau = W(k0) seconds
    x, w = i["k0"], 0.5
    for _ in range(100):
        w -= (w * math.exp(w) - x) / (math.exp(w) * (w + 1))
    return {"tau": w}


def symbolic():
    import sympy as sp
    k0 = sp.symbols("k0", positive=True)
    return {"tau": sp.LambertW(k0)}
