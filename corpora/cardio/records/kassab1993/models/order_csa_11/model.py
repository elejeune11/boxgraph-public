import math


def run(inputs, settings):
    n = int(round(inputs["n"]))
    if not 1 <= n <= 11:
        raise ValueError(f"order {n} outside 1-11")
    d = inputs[f"D{n}"] * 1e-4  # um -> cm
    return {"A": math.pi / 4 * d ** 2 * inputs[f"N{n}"]}
