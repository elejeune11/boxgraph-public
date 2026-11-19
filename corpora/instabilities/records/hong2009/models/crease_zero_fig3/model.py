import numpy as np


def run(inputs, settings):
    # f(eps_c) = 0: the curve stops just above zero, so extend a straight line
    # through its last n points to f = 0.
    x = np.asarray(inputs["f"]["x"], dtype=float)
    y = np.asarray(inputs["f"]["y"], dtype=float)
    order = np.argsort(x)
    x, y = x[order], y[order]
    n = int(settings.get("n_last", 2))
    a, b = np.polyfit(x[-n:], y[-n:], 1)
    return {"eps_c": float(-b / a)}
