import math

ORDERS = list(range(1, 11))


def run(inputs, settings):
    # mm^3 -> ml: 1e-3
    v = sum(inputs[f"L{n}"] * math.pi / 4 * inputs[f"D{n}"] ** 2 * inputs[f"N{n}"] for n in ORDERS)
    return {"V": v * 1e-3}
