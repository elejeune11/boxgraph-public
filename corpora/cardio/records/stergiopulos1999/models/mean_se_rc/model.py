"""Mean and standard error (sd with n - 1, over sqrt(n)) of seven values; `bar` only labels the bar."""
import math


def run(inputs, settings):
    x = [inputs[f"x{i}"] for i in range(1, 8)]
    n = len(x)
    m = sum(x) / n
    sd = math.sqrt(sum((v - m) ** 2 for v in x) / (n - 1))
    return {"mean": m, "se": sd / math.sqrt(n)}
