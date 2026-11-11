# Combine two groups' means and sample SDs (n - 1) into the whole sample's mean and sample SD.
# Not an equation of the paper: the arithmetic that makes its whole-cohort and group values consistent.
import math


def run(inputs, settings):
    N, n1 = inputs["N"], inputs["n1"]
    n2 = N - n1
    m1, s1, m2, s2 = inputs["m1"], inputs["s1"], inputs["m2"], inputs["s2"]
    mean = (n1 * m1 + n2 * m2) / N
    var = ((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2 + n1 * n2 * (m1 - m2) ** 2 / N) / (N - 1)
    return {"mean": mean, "sd": math.sqrt(var)}
