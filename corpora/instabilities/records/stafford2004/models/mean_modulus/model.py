"""The unweighted mean of the plotted moduli (the paper does not say how its 3.4 GPa is formed)."""


def run(inputs, settings):
    ys = [y for y in inputs["E"]["y"] if y is not None]
    return {"E_mean": sum(ys) / len(ys)}
