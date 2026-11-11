# Pearson's r of a per-subject scatter (one marker per subject). r does not change under a linear relabelling
# of either axis, so it tests the plotted points whatever the axis labels mean. Units: x in years, y in percent.
import math


def run(inputs, settings):
    x, y = inputs["Y"]["x"], inputs["Y"]["y"]
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return {"r": sxy / math.sqrt(sxx * syy)}
