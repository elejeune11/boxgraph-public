"""Two-sided paired t-test over seven pairs (x_i, y_i)."""
import math

from scipy import stats


def run(inputs, settings):
    d = [inputs[f"x{i}"] - inputs[f"y{i}"] for i in range(1, 8)]
    n = len(d)
    mean = sum(d) / n
    sd = math.sqrt(sum((v - mean) ** 2 for v in d) / (n - 1))
    t = mean / (sd / math.sqrt(n))
    return {"p": float(2 * stats.t.sf(abs(t), n - 1))}
