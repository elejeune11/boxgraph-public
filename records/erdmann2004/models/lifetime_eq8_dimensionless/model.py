from math import comb


def run(inputs, settings):
    n0, g = int(round(inputs["N0"])), inputs["gamma"]
    s = sum(comb(n0, n) * g**n / n for n in range(1, n0 + 1))
    h = sum(1.0 / i for i in range(1, n0 + 1))
    return {"T": (s + h) / (1 + g)}
