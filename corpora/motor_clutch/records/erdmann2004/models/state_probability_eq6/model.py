import math


def run(inputs, settings):
    # Eq. 6 as printed: the factor e^{-r(j) tau} stands inside the product over k != j, so it
    # appears once per factor (N0 - i times). For i = 0, r(0) = 0 is part of the product (Eq. 2).
    n0, i, f, tau = int(round(inputs["N0"])), int(round(inputs["i"])), inputs["f"], inputs["tau"]

    def r(j):
        return j * math.exp(f / j) if j > 0 else 0.0

    pre = math.prod(r(j) for j in range(i + 1, n0 + 1))
    s = sum(math.prod(math.exp(-r(j) * tau) / (r(k) - r(j)) for k in range(i, n0 + 1) if k != j)
            for j in range(i, n0 + 1))
    return {"p": pre * s}
