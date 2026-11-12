"""Pearson's correlation coefficient of the plotted points."""
import math


def run(inputs, settings):
    xs, ys = inputs["pts"]["x"], inputs["pts"]["y"]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return {"r": sxy / math.sqrt(sxx * syy)}
