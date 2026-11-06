# Eq. 21 solved for gamma in (0, 1] (gamma = (r_d2/r_d1)^2 with d2 the smaller daughter).
# eta(gamma) increases monotonically on (0, 1] for xi > 2, so the root found by bisection is unique.


def _eta(g, xi):
    return (1 + g) / (1 + g ** (xi / 2)) ** (2 / xi)


def run(inputs, settings):
    xi, eta = inputs["xi"], inputs["eta"]
    lo, hi = 1e-12, 1.0
    if not (_eta(lo, xi) <= eta <= _eta(hi, xi)):
        return {"gamma": None}
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if _eta(mid, xi) < eta:
            lo = mid
        else:
            hi = mid
    return {"gamma": 0.5 * (lo + hi)}
