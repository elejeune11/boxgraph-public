# Pearson's r of the per-participant points of Supplemental Fig. 2. r does not change under a linear relabelling of either
# axis. x in mL/mL, y in mL/mL; r dimensionless.
import math


def run(inputs, settings):
    x, y = list(inputs["A"]["x"]), list(inputs["A"]["y"])
    x += list(inputs["B"]["x"])
    y += list(inputs["B"]["y"])
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    r = sxy / math.sqrt(sxx * syy)
    return {"R2": r * r}
