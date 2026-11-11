# Group statistics of a per-subject scatter (one marker per subject): the subjects are split at a threshold
# of the x quantity (x <= threshold: low group, x > threshold: high group); each group's mean of x and of y,
# and Pearson's r of y on x over all markers. Units: x in cm, y in percent.
import math


def _r(x, y):
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy)


def run(inputs, settings):
    x, y = inputs["Y"]["x"], inputs["Y"]["y"]
    th = float(settings["threshold_cm"])
    lo = [(a, b) for a, b in zip(x, y) if a <= th]
    hi = [(a, b) for a, b in zip(x, y) if a > th]
    m = lambda pts, i: sum(p[i] for p in pts) / len(pts)
    return {"y_low": m(lo, 1), "y_high": m(hi, 1), "x_low": m(lo, 0), "x_high": m(hi, 0),
            "n_high": float(len(hi)), "r": _r(x, y)}
