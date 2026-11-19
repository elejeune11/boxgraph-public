# Least-squares slope of N against t, unweighted, over every plotted mean (the paper does not
# say how its rate was fitted: per capsule or on the means; question q_growth_rate_fit).


def run(inputs, settings):
    t, n = inputs["N"]["x"], inputs["N"]["y"]
    k = len(t)
    tm, nm = sum(t) / k, sum(n) / k
    sxy = sum((a - tm) * (b - nm) for a, b in zip(t, n))
    sxx = sum((a - tm) ** 2 for a in t)
    return {"rate": sxy / sxx}
