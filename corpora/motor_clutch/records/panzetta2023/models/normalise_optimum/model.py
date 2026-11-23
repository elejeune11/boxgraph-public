# Fig. 8A from Fig. 6: the optimal nc divided by the optimal nc at no residual strain, given at the
# strains of a second curve (the Fig. 8A reading), by linear interpolation in strain of the first.
import numpy as np


def run(inputs, settings):
    x = np.asarray(inputs["n"]["x"], float)
    y = np.asarray(inputs["n"]["y"], float)
    order = np.argsort(x)
    x, y = x[order], y[order]
    out = []
    for g in inputs["grid"]["x"]:
        out.append(float(np.interp(g, x, y)) / inputs["n_ref"] if x[0] <= g <= x[-1] else None)
    return {"r": {"x": list(inputs["grid"]["x"]), "y": out}}
