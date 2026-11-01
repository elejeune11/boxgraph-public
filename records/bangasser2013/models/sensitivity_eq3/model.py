# Eq. 3: S is the slope of a least-squares line through (log c_j, log k_j), j = 1..5.
# The slope does not depend on the base of the log, nor on multiplying p by p0.
import math


def run(inputs, settings):
    xs = [math.log10(inputs[f"c{j}"]) for j in range(1, 6)]
    ys = [math.log10(inputs[f"k{j}"]) for j in range(1, 6)]
    mx, my = sum(xs) / 5, sum(ys) / 5
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    return {"S": sxy / sxx}
