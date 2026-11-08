# Least-squares straight line through (n, log10 y_n), n = Strahler order (Horton's law).
# Port units: dimensionless; the constants refer to log10 of the value in these units.
import math

ORDERS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def run(inputs, settings):
    xs = ORDERS
    ys = [math.log10(inputs[f"N{n}"]) for n in ORDERS]
    k = len(xs)
    mx, my = sum(xs) / k, sum(ys) / k
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    a = my - b * mx
    r2 = sxy * sxy / (sxx * syy)
    return {"a": a, "b": b, "R2": r2, "ratio": 10 ** (-b)}
