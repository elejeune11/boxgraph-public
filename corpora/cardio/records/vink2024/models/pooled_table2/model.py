# Mean and sample SD of the union of two groups from each group's n, mean and SD.
# Every variable stays in its own port unit; counts are dimensionless.
import math

VARS = ["age", "bmi", "ef", "cfr", "hr0", "hrmax"]


def _pool(n1, m1, s1, n2, m2, s2):
    n = n1 + n2
    m = (n1 * m1 + n2 * m2) / n
    ss = (n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2 + n1 * n2 / n * (m1 - m2) ** 2
    return m, math.sqrt(ss / (n - 1))


def run(inputs, settings):
    out = {}
    for v in VARS:
        m, s = _pool(inputs["n1"], inputs[v + "_m1"], inputs[v + "_s1"], inputs["n2"], inputs[v + "_m2"], inputs[v + "_s2"])
        out[v + "_m"], out[v + "_s"] = m, s
    return out


def symbolic():
    import sympy as sp
    n1, n2 = sp.symbols("n1 n2", positive=True)
    out = {}
    for v in VARS:
        m1, s1, m2, s2 = sp.symbols(f"{v}_m1 {v}_s1 {v}_m2 {v}_s2", positive=True)
        n = n1 + n2
        out[v + "_m"] = (n1 * m1 + n2 * m2) / n
        out[v + "_s"] = sp.sqrt(((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2 + n1 * n2 / n * (m1 - m2) ** 2) / (n - 1))
    return out
