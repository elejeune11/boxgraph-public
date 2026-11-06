# Mean and standard deviation of n = 9 per-dog values, as in the MEAN ± SD rows of Table 2.
import math

N = 9


def run(inputs, settings):
    xs = [inputs[f"x{i}"] for i in range(1, N + 1)]
    ddof = inputs["ddof"]
    m = sum(xs) / N
    ss = sum((x - m) ** 2 for x in xs)
    return {"mean": m, "sd": math.sqrt(ss / (N - ddof))}


def symbolic():
    import sympy as sp
    xs = sp.symbols("x1:10", real=True)
    ddof = sp.Symbol("ddof", nonnegative=True)
    m = sum(xs) / N
    return {"mean": m, "sd": sp.sqrt(sum((x - m) ** 2 for x in xs) / (N - ddof))}
