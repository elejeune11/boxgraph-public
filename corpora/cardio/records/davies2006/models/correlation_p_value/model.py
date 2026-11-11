# Standard significance test of a Pearson r (the paper names only "Statview 5.0"; this is the usual test).
# Not an equation of the paper: the arithmetic that links its printed r and P.
import math


def run(inputs, settings):
    from scipy import stats

    r, n = inputs["r"], inputs["n"]
    df = n - 2
    t = abs(r) * math.sqrt(df) / math.sqrt(1.0 - r * r)
    return {"p": float(2.0 * stats.t.sf(t, df))}
