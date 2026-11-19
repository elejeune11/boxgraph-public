def run(inputs, settings):
    # positive real root of zeta^3 + 2 zeta^2 - 2 = 0, by bisection on [0, 1] (f(0) < 0 < f(1))
    def f(z):
        return z**3 + 2 * z**2 - 2

    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return {"zeta": 0.5 * (lo + hi)}
