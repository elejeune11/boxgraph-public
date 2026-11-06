# Mean and sample SD of the relative discrepancy |model - in vivo| / denominator over all locations, in %.
# The paper does not say what the difference is relative to: the denominator is (1 - w) * in vivo + w * model,
# with w an added input (q_discrepancy_norm).
import math


def run(inputs, settings):
    n = sum(1 for k in inputs if k.startswith("v"))
    w = inputs["w"]
    e = []
    for i in range(1, n + 1):
        v, m = inputs[f"v{i}"], inputs[f"m{i}"]
        e.append(100.0 * abs(m - v) / ((1.0 - w) * v + w * m))
    mean = sum(e) / n
    sd = math.sqrt(sum((x - mean) ** 2 for x in e) / (n - 1))
    return {"mean": mean, "sd": sd}
