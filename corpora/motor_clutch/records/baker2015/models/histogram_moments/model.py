# Moments of a binned histogram: bins at centres d (um) with frequencies p (percent).
import math


def run(inputs, settings):
    c = inputs["p"]
    pts = [(x, y) for x, y in zip(c["x"], c["y"]) if x is not None and y is not None]
    w = sum(y for _, y in pts)
    mean = sum(x * y for x, y in pts) / w
    var = sum((x - mean) ** 2 * y for x, y in pts) / w
    return {"mean": mean, "sd": math.sqrt(var)}
